from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.blog import Blog
from app.serialization import blog_to_dict

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.get("")
def list_blogs(db: Session = Depends(get_db)):
    blogs = db.query(Blog).order_by(Blog.scraped_at.desc()).all()
    return {"count": len(blogs), "data": [blog_to_dict(b) for b in blogs]}


@router.get("/{blog_id}")
def get_blog(blog_id: UUID, db: Session = Depends(get_db)):
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog_to_dict(blog)
