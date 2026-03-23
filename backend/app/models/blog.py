from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.orm import relationship
from ..db.database import Base
from .base.base_model import BaseModel

class Blog(Base, BaseModel):
    __tablename__ = "blogs"

    source = Column(String)
    url = Column(String, unique=True)
    title = Column(String)
    scraped_at = Column(DateTime)
    published_at = Column(DateTime, nullable=True)
    content = Column(Text)
    author = Column(String, nullable=True)

    # One blog post can have many sentiment runs (re-scrape / re-analyze over time).
    sentiments = relationship(
        "Sentiment",
        back_populates="blog",
        cascade="all, delete-orphan",
    )

