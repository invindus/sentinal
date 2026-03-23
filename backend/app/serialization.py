# Bridge between database models and API responses
from datetime import datetime

from app.models.blog import Blog

# placeholder datetime used only in sorting
_EPOCH = datetime(1970, 1, 1)


def _sentiment_to_dict(s):
    return {
        "id": str(s.id),
        "score": s.score,
        "label": s.label,
        "emotion": s.emotion,
        "analyzed_at": s.analyzed_at.isoformat() if s.analyzed_at else None,
    }


def blog_to_dict(blog: Blog) -> dict:
    sentiments = sorted(
        blog.sentiments,
        key=lambda x: x.analyzed_at if x.analyzed_at is not None else _EPOCH, # sort by analyzed_at, most recent first. EPOCH is a placeholder for None values
        reverse=True,
    )
    return {
        "id": str(blog.id),
        "source": blog.source,
        "url": blog.url,
        "title": blog.title,
        "author": blog.author,
        "scraped_at": blog.scraped_at.isoformat() if blog.scraped_at else None,
        "published_at": blog.published_at.isoformat() if blog.published_at else None,
        "content": blog.content,
        "sentiments": [_sentiment_to_dict(s) for s in sentiments],
    }
