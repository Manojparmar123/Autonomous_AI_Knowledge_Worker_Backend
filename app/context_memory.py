from sqlmodel import Session, select
from .db import get_session
from .models import ContextMemory
import json
from datetime import datetime
from typing import Dict, Any, List


def get_context_history(session_id: str, session: Session) -> List[Dict[str, Any]]:
    """
    Retrieve full context history for a session ID.
    Returns a list of all context snapshots (dicts).
    """
    context_entries = session.exec(
        select(ContextMemory).where(ContextMemory.session_id == session_id)
    ).all()

    return [
        {
            "id": entry.id,
            "context": json.loads(entry.context_data),
            "last_updated": entry.last_updated.isoformat()
        }
        for entry in context_entries
    ]


def get_latest_context(session_id: str, session: Session) -> dict:
    """
    Retrieve the latest context for a session ID.
    """
    context_entry = session.exec(
        select(ContextMemory)
        .where(ContextMemory.session_id == session_id)
        .order_by(ContextMemory.last_updated.desc())
    ).first()

    if context_entry:
        return json.loads(context_entry.context_data)
    return {}


def get_context(session_id: str, session: Session) -> dict:
    """
    Backward-compatible wrapper for get_latest_context.
    Returns the latest context for a given session.
    """
    return get_latest_context(session_id, session)


def save_context(session_id: str, context_data: dict, session: Session) -> dict:
    """
    Save new context snapshot for a session ID.
    No embeddings, just raw JSON stored in DB.
    """
    context_json = json.dumps(context_data)

    context_entry = ContextMemory(
        session_id=session_id,
        context_data=context_json,
        last_updated=datetime.utcnow()
    )
    session.add(context_entry)

    try:
        session.commit()
        session.refresh(context_entry)
    except Exception as e:
        session.rollback()
        raise e

    return json.loads(context_entry.context_data)


def search_context(query: str, session: Session, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Simple keyword search across stored contexts (fallback without embeddings).
    """
    context_entries = session.exec(select(ContextMemory)).all()
    results = []

    for entry in context_entries:
        data = json.loads(entry.context_data)
        text_repr = json.dumps(data).lower()
        if query.lower() in text_repr:
            results.append({
                "id": entry.id,
                "session_id": entry.session_id,
                "context": data,
                "last_updated": entry.last_updated.isoformat()
            })

    return results[:top_k]


