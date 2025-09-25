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
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Async database URL (aiosqlite)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./database.db")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}  # needed for SQLite
)

# Async session factory
async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Async DB initialization (creates tables)
async def async_init_db():
    from .models import Document, Insight, Run, Task, Report  # noqa
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency to get async session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
