from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, List, Optional
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.blog import Blog
from app.models.sentiment import Sentiment
from app.services.sentiment import analyze_text

# RSS feed makes it easier to scrape the latest post from the feed.
NVIDIA_FEED_URL = "https://blogs.nvidia.com/feed/"


def _strip_xml_namespaces(elem: ET.Element) -> None:
    """Strip XML namespaces from the element."""
    for el in elem.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]


def parse_nvidia_feed_xml(xml_text: str) -> List[dict]:
    """Parse NVIDIA WordPress RSS; returns list of {title, link, pub_date_raw, categories}."""
    root = ET.fromstring(xml_text)
    _strip_xml_namespaces(root)

    channel = root.find("channel")
    if channel is None:
        return []

    items: List[dict] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_raw = (item.findtext("pubDate") or "").strip()

        categories = []

        for cat in item.findall("category"):
            if cat.text:
                categories.append(cat.text.strip())
        if link:
            items.append(
                {
                    "title": title,
                    "link": link,
                    "pub_date_raw": pub_raw or None,
                    "categories": categories,
                }
            )
    return items


def fetch_nvidia_feed(limit: Optional[int] = None) -> List[dict]:
    """GET the RSS feed and return up to `limit` entries (newest first)."""
    response = requests.get(NVIDIA_FEED_URL, timeout=30)
    response.raise_for_status()
    items = parse_nvidia_feed_xml(response.text)
    if limit is not None:
        return items[:limit]
    return items


def _parse_rss_pub_date(raw: Optional[str]) -> Optional[datetime]:
    """Parse the published date from the RSS feed."""
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None


def scrape_article_url(url: str, rss_meta: Optional[dict] = None) -> dict:
    """
    Scrape a single NVIDIA blog article page (same layout as blogs.nvidia.com/blog/...).
    rss_meta may include title, pub_date_raw, categories from the feed.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("article")
    if not article:
        raise ValueError("Could not find article on page")

    title_el = article.find("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    time_tag = article.find("time")
    published_raw = time_tag.get("datetime") if time_tag else None

    author_tag = article.find("span", class_="author")
    author = author_tag.get_text(strip=True) if author_tag else None

    content = article.find("div", class_="entry-content")
    if not content:
        raise ValueError("Could not find entry-content on page")

    paragraphs = [
        p.get_text(strip=True) for p in content.find_all("p") if p.get_text(strip=True)
    ]

    if rss_meta:
        if not title and rss_meta.get("title"):
            title = rss_meta["title"]
        if not published_raw and rss_meta.get("pub_date_raw"):
            published_raw = rss_meta["pub_date_raw"]

    return {
        "source": "nvidia_blog",
        "url": url,
        "title": title,
        "author": author,
        "published_at": published_raw,
        "content": paragraphs,
        "categories": (rss_meta or {}).get("categories") or [],
    }


def scrape_blog():
    """Backward-compatible: scrape the latest post from the feed."""
    entries = fetch_nvidia_feed(limit=1)
    if not entries:
        raise ValueError("NVIDIA feed returned no items")
    e = entries[0]
    return scrape_article_url(e["link"], rss_meta=e)


def _parse_published_at(raw: Optional[str]):
    """Parse the published date from the blog post."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return _parse_rss_pub_date(raw)


def _paragraphs_to_text(paragraphs: List[str]) -> str:
    return "\n\n".join(paragraphs)


def ingest_blog_append_sentiment(db: Session, data: dict) -> Blog:
    """Update or create the blog row, then append a new Sentiment row (history)."""
    text = _paragraphs_to_text(data["content"])
    sentiment_payload = analyze_text(text)
    now = datetime.now(timezone.utc)
    published_at = _parse_published_at(data.get("published_at"))

    blog = db.query(Blog).filter(Blog.url == data["url"]).first()

    if blog:
        blog.source = data["source"]
        blog.title = data["title"]
        blog.author = data.get("author")
        blog.published_at = published_at
        blog.content = text
        blog.scraped_at = now
    else:
        blog = Blog(
            source=data["source"],
            url=data["url"],
            title=data["title"],
            author=data.get("author"),
            published_at=published_at,
            content=text,
            scraped_at=now,
        )
        db.add(blog)
        db.flush()

    db.add(
        Sentiment(
            blog_id=blog.id,
            score=sentiment_payload["score"],
            label=sentiment_payload["label"],
            emotion=sentiment_payload["emotion"],
            analyzed_at=sentiment_payload["analyzed_at"],
        )
    )
    db.commit()
    db.refresh(blog)
    return blog


def ingest_nvidia_feed(
    db: Session,
    limit: int = 10,
) -> dict[str, Any]:
    """
    For each of the first `limit` feed entries, fetch the article and persist + sentiment.
    Returns summary with per-URL status (ok or error message).
    """
    entries = fetch_nvidia_feed(limit=limit)
    results: List[dict] = []
    errors: List[dict] = []

    for entry in entries:
        url = entry["link"]
        try:
            data = scrape_article_url(url, rss_meta=entry)
            blog = ingest_blog_append_sentiment(db, data)
            results.append({"url": url, "blog_id": str(blog.id), "title": blog.title})
        except Exception as exc:
            errors.append({"url": url, "detail": str(exc)})

    return {
        "feed_url": NVIDIA_FEED_URL,
        "attempted": len(entries),
        "ingested": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }
