from datetime import datetime, timezone
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.models.blog import Blog
from app.models.sentiment import Sentiment
from app.services.sentiment import analyze_text


def scrape_blog():
    url = "https://blogs.nvidia.com/blog/2026-ces-special-presentation/"
    response = requests.get(url, timeout=10)
    response.raise_for_status() # raise an exception if the response is not successful
    soup = BeautifulSoup(response.text, "html.parser") # parse the response text as HTML

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

    paragraphs = [p.get_text(strip=True) for p in content.find_all("p") if p.get_text(strip=True)]

    return {
        "source": "nvidia_blog",
        "url": url,
        "title": title,
        "author": author,
        "published_at": published_raw,
        "content": paragraphs,
    }

# get the published at date from the raw data
def _parse_published_at(raw: Optional[str]):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None

# convert the paragraphs to a single text string
def _paragraphs_to_text(paragraphs: List[str]) -> str:
    return "\n\n".join(paragraphs)

# full function to analyze blog and append sentiment
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
