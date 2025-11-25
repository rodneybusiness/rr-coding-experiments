"""
Database Session Management

Provides database connection and session management for SQLAlchemy 2.0.
Supports both sync and async patterns.
"""

from typing import AsyncGenerator, Generator
from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.base import Base


# === Sync Database Engine ===
# For use with traditional synchronous code

SQLALCHEMY_DATABASE_URL = getattr(settings, 'DATABASE_URL', 'sqlite:///./film_financing.db')

# Convert postgres:// to postgresql:// for SQLAlchemy 2.0
if SQLALCHEMY_DATABASE_URL.startswith('postgres://'):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Create sync engine
sync_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=getattr(settings, 'SQL_ECHO', False),
)

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency injection for sync database sessions.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for sync database sessions.

    Usage:
        with get_db_context() as db:
            db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Async Database Engine ===
# For use with async code (recommended for FastAPI)

ASYNC_DATABASE_URL = getattr(settings, 'ASYNC_DATABASE_URL', None)

# Derive async URL from sync URL if not provided
if ASYNC_DATABASE_URL is None:
    if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
        ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')
    else:
        ASYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
elif ASYNC_DATABASE_URL.startswith('sqlite'):
    # Handle SQLite for async (use aiosqlite)
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace('sqlite:///', 'sqlite+aiosqlite:///')

# Create async engine (only if not SQLite in sync mode)
try:
    async_engine = create_async_engine(
        ASYNC_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=getattr(settings, 'SQL_ECHO', False),
    )

    # Create async session factory
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )

    async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Dependency injection for async database sessions.

        Usage:
            @app.get("/items")
            async def get_items(db: AsyncSession = Depends(get_async_db)):
                result = await db.execute(select(Item))
                return result.scalars().all()
        """
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    @asynccontextmanager
    async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
        """
        Context manager for async database sessions.

        Usage:
            async with get_async_db_context() as db:
                result = await db.execute(select(Item))
                return result.scalars().all()
        """
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

except Exception:
    # Async not available (e.g., missing asyncpg)
    async_engine = None
    AsyncSessionLocal = None

    async def get_async_db():
        raise NotImplementedError("Async database not configured")

    async def get_async_db_context():
        raise NotImplementedError("Async database not configured")


# === Database Initialization ===

def init_db() -> None:
    """
    Initialize database tables.
    Creates all tables defined in the models.
    """
    from app.db.models import Base as ModelsBase  # Use Base from models
    ModelsBase.metadata.create_all(bind=sync_engine)


async def init_async_db() -> None:
    """
    Initialize database tables asynchronously.
    """
    if async_engine is None:
        init_db()
        return

    from app.db.models import Base as ModelsBase  # Use Base from models
    async with async_engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)


def drop_all_tables() -> None:
    """
    Drop all database tables.
    USE WITH CAUTION - Only for testing/development.
    """
    Base.metadata.drop_all(bind=sync_engine)


# === Connection Testing ===

def test_connection() -> bool:
    """Test database connection."""
    from sqlalchemy import text
    try:
        with sync_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def test_async_connection() -> bool:
    """Test async database connection."""
    from sqlalchemy import text
    if async_engine is None:
        return test_connection()
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
