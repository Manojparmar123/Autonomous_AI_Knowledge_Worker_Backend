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
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import os

# ------------------- Database URLs -------------------
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
ASYNC_DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

# ------------------- Engines -------------------
# Sync engine for existing endpoints
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# Async engine for startup (async-safe)
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=False, connect_args=connect_args)

# ------------------- DB Initialization -------------------
def init_db():
    """Sync DB init (existing)"""
    from .models import Document, Insight, Run, Task, Report  # noqa
    SQLModel.metadata.create_all(engine)

async def async_init_db():
    """Async-safe DB init (for Railway / aiosqlite)"""
    from .models import Document, Insight, Run, Task, Report  # noqa
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# ------------------- Sessions -------------------
# Sync session (existing)
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

# Async session (optional if needed in future)
def get_async_session():
    async_session = AsyncSession(async_engine)
    try:
        yield async_session
    finally:
        pass
