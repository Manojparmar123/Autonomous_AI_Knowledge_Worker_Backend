import sys
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# Add your app directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.models import SQLModel  # your models
from app.models import Run, Task, Document, Insight, Report, User, ContextMemory

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Point to your models
target_metadata = SQLModel.metadata

# Use DATABASE_URL from settings
def get_url():
    return settings.DATABASE_URL  # e.g., "sqlite+aiosqlite:///./app.db"

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async def do_run_migrations():
        async with connectable.connect() as connection:
            # Configure context and run migrations in sync wrapper
            def sync_run_migrations(conn: Connection):
                context.configure(
                    connection=conn,
                    target_metadata=target_metadata
                )
                with context.begin_transaction():
                    context.run_migrations()

            await connection.run_sync(sync_run_migrations)

    import asyncio
    asyncio.run(do_run_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
