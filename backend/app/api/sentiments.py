from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.sentiment import Sentiment

router = APIRouter(prefix="/sentiments", tags=["sentiments"])


@router.get("/")
def get_all_sentiments(db: Session = Depends(get_db)):
    return db.query(Sentiment).order_by(Sentiment.analyzed_at.desc()).all()
