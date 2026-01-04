from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.database import Base
from .base.base_model import BaseModel

class Blog(Base, BaseModel):
    __tablename__ = "blogs"

    source = Column(String)
    url = Column(String)
    scraped_at = Column(DateTime)
    raw_text = Column(String)

    sentiment = relationship("Sentiment", back_populates="blog")

class Sentiment(Base, BaseModel):
    __tablename__ = "sentiment"

    blog_id = Column(UUID(as_uuid=True), ForeignKey("blogs.id"))
    
    score = Column(Float)
    label = Column(String)
    emotion = Column(String)
    analyzed_at = Column(DateTime)

    blog = relationship("Blog", back_populates="sentiment")

