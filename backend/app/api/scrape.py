from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.serialization import blog_to_dict
from app.services.scrape import ingest_blog_append_sentiment, scrape_blog

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.get("/nvidia")
def scrape_nvidia_preview():
    """Scrape only; no database write."""
    try:
        data = scrape_blog()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/nvidia")
def scrape_nvidia_ingest(db: Session = Depends(get_db)):
    """Scrape, update blog row, append a new Sentiment row (history)."""
    try:
        data = scrape_blog()
        blog = ingest_blog_append_sentiment(db, data)
        return {"status": "success", "data": blog_to_dict(blog)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
