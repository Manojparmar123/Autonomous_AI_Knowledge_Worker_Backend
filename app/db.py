# apps/backend/app/db.py
from sqlmodel import SQLModel, create_engine, Session
import os

# Use a single consistent SQLite DB file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# SQLite requires this for multithreading
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create engine (sync)
engine = create_engine(DATABASE_URL, echo=False, connect_args=connect_args)

# Init DB (creates tables)
def init_db():
    from .models import Document, Insight, Run, Task, Report  # noqa
    SQLModel.metadata.create_all(engine)

# Get DB session (sync) as a generator
def get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
