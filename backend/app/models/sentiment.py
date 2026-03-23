from sqlalchemy import Column, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
from .base.base_model import BaseModel

class Sentiment(Base, BaseModel):
    __tablename__ = "sentiment"

    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id"), nullable=False)

    score = Column(Float)
    label = Column(String)
    emotion = Column(String)
    analyzed_at = Column(DateTime)

    blog = relationship("Blog", back_populates="sentiments")

    __table_args__ = (Index("ix_sentiment_blog_analyzed_at", "blog_id", "analyzed_at"),) # index on blog_id and analyzed_at for faster queries

