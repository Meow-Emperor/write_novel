from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings


# Configure connection pool and engine parameters
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# Engine configuration with connection pooling
engine_kwargs = {
    "connect_args": connect_args,
    "pool_pre_ping": True,  # Verify connections before using them
    "echo": settings.DEBUG,  # Log SQL queries in debug mode
}

# Add pool configuration for non-SQLite databases
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": 10,  # Number of connections to maintain
        "max_overflow": 20,  # Additional connections when pool is full
        "pool_timeout": 30,  # Seconds to wait for a connection
        "pool_recycle": 3600,  # Recycle connections after 1 hour
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator:
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
