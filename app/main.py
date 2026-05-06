"""
main.py
-------
Entry point for the Address Book FastAPI application.

Responsibilities:
  - Configure application-wide logging.
  - Create database tables on startup (if they don't exist).
  - Register API routers.
  - Set application metadata (title, description, version) for Swagger UI.
"""

import logging
import logging.config

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine
from app.models import Base
from app.routers import addresses



LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d — %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
    # Set individual module log levels here if needed
    "loggers": {
        "app": {"level": "DEBUG", "propagate": True},
        "uvicorn.access": {"level": "INFO", "propagate": True},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Code before `yield` runs on startup; code after `yield` runs on shutdown.

    Startup:
      - Creates all database tables defined in ORM models (if they don't exist yet).

    Shutdown:
      - Placeholder for cleanup logic (e.g., closing connection pools).
    """
    logger.info("Starting up Address Book API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
    yield
    logger.info("Shutting down Address Book API.")



app = FastAPI(
    title="Address Book API",
    description=(
        "A RESTful API for managing an address book. "
        "Supports creating, updating, deleting, and retrieving addresses. "
        "Addresses can also be queried by geographic proximity using the Haversine formula.\n\n"
        "**Database**: SQLite (file: `address_book.db`)\n"
        "**Coordinates**: Latitude (-90 to 90), Longitude (-180 to 180)"
    ),
    version="1.0.0",
    contact={
        "name": "Address Book API",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan,
)


app.include_router(addresses.router)

logger.info("Address Book API is ready. Visit /docs for the Swagger UI.")
