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

Base.metadata.create_all(bind=engine) # remove this after initial create, use alembic migrations

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()