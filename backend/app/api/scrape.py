from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.serialization import blog_to_dict
from app.services.scrape import (
    fetch_nvidia_feed,
    ingest_blog_append_sentiment,
    ingest_nvidia_feed,
    scrape_blog,
)

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.get("/nvidia")
def scrape_nvidia_preview():
    """Scrape latest feed article only; no database write."""
    try:
        data = scrape_blog()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/nvidia")
def scrape_nvidia_ingest(db: Session = Depends(get_db)):
    """Ingest the latest post from the NVIDIA RSS feed (one article)."""
    try:
        data = scrape_blog()
        blog = ingest_blog_append_sentiment(db, data)
        return {"status": "success", "data": blog_to_dict(blog)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/nvidia/feed")
def nvidia_feed_preview(
    limit: int = Query(20, ge=1, le=100, description="Max items to list from RSS"),
):
    """Return entries from https://blogs.nvidia.com/feed/ without scraping HTML."""
    try:
        entries = fetch_nvidia_feed(limit=limit)
        return {
            "status": "success",
            "count": len(entries),
            "data": entries,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/nvidia/feed")
def nvidia_feed_ingest(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="How many newest posts to scrape and store"),
):
    """Scrape multiple posts from the NVIDIA RSS feed, analyze sentiment, save each."""
    try:
        summary = ingest_nvidia_feed(db, limit=limit)
        return {"status": "success", **summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
