from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,     # before connecting, check if its alive. if dead, discard and make new one
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _register_models(): 
    from app.models.blog import Blog  # noqa: F401 - ignore unused imports for linting
    from app.models.sentiment import Sentiment  # noqa: F401


_register_models()
Base.metadata.create_all(bind=engine)  # remove after Alembic migrations

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()