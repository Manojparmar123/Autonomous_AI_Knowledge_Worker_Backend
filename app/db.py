# # apps/backend/app/db.py
# from sqlmodel import SQLModel, create_engine, Session
# import os

# # Use a single consistent SQLite DB file
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# # SQLite requires this for multithreading
# connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# # Create engine (sync)
# engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# # Init DB (creates tables)
# def init_db():
#     from .models import Document, Insight, Run, Task, Report  # noqa
#     SQLModel.metadata.create_all(engine)

# # Get DB session (sync) as a generator
# def get_session():
#     session = Session(engine)
#     try:
#         yield session
#     finally:
#         session.close()
# apps/backend/app/db.py

import os
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Database URL (async for async operations)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")

# --------------------
# Async engine & session
# --------------------
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def async_init_db():
    """Initialize async DB (create tables)"""
    from .models import Document, Insight, Run, Task, Report  # noqa
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async session"""
    async with async_session() as session:
        yield session

# --------------------
# Sync engine (for code that expects 'engine')
# --------------------
# Remove '+aiosqlite' for sync engine
SYNC_DATABASE_URL = DATABASE_URL.replace("+aiosqlite", "")
engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False
)
