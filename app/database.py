

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

DATABASE_URL = "sqlite:///./address_book.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,  
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class that all ORM models will inherit from."""
    pass


def get_db():
    """
    FastAPI dependency that yields a database session per request.
    Ensures the session is always closed after the request completes,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        logger.debug("Database session opened.")
        yield db
    finally:
        db.close()
        logger.debug("Database session closed.")
