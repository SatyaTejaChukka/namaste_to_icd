"""
Database configuration and connection management for async operations.
Production-ready SQLAlchemy setup with async support and connection pooling.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
import logging
from config import config

logger = logging.getLogger(__name__)

# --- Database Configuration ---
# Try PostgreSQL first, fallback to SQLite
try:
    DATABASE_URL = config.ASYNC_DATABASE_URL
    logger.info(f"Connecting to PostgreSQL database: {config.DB_NAME}")
except Exception as e:
    DATABASE_URL = config.SQLITE_URL
    logger.warning(f"PostgreSQL connection failed, using SQLite: {config.SQLITE_DB_NAME}")

# Create an asynchronous SQLAlchemy engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False
)

# Create an async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injector that provides an async database session
    and ensures it's closed afterward.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()