from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field
import uuid

def utc_now():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

# ----------------- Run Table -----------------
class Run(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    status: str
    job_type: str
    state_log: Optional[str] = None
    started_at: datetime = Field(default_factory=utc_now)
    finished_at: Optional[datetime] = None
    task_id: Optional[str] = Field(default=None, foreign_key="task.id")

# ----------------- Task Table -----------------
class Task(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    run_id: str = Field(foreign_key="run.id")
    kind: str
    payload: Optional[str] = None
    status: Optional[str] = None
    detail: Optional[str] = None

# ----------------- Document Table -----------------
class Document(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    source: str
    title: str
    url: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)

# ----------------- Insight Table -----------------
class Insight(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    document_id: str = Field(foreign_key="document.id")
    summary: str
    created_at: datetime = Field(default_factory=utc_now)

# ----------------- Report Table -----------------
class Report(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    kind: str
    content: str
    created_at: datetime = Field(default_factory=utc_now)

# ----------------- Context Memory -----------------
class ContextMemory(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    session_id: str = Field(index=True)
    context_data: Optional[str] = None
    last_updated: datetime = Field(default_factory=utc_now)

# ----------------- User Table -----------------
class User(SQLModel, table=True):
    id: str = Field(default_factory=generate_uuid, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False)
    name: Optional[str] = None
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

# ----------------- End of Models -----------------
