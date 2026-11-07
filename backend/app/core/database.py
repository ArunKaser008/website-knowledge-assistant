#This file creates the SQLAlchemy engine and database session factory.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Create SQLAlchemy database engine.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


# Create database session factory.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# Database dependency for FastAPI endpoints.
def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()