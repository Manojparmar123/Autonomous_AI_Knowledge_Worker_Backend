from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import time

router = APIRouter(prefix="/memory", tags=["memory"])

# Simple in-memory store (can swap with DB later)
_store: Dict[str, Any] = {}
_events: Dict[str, List[Dict[str, Any]]] = {}

class PutItem(BaseModel):
    key: str
    value: Dict[str, Any]

class AppendEvent(BaseModel):
    key: str
    event: Dict[str, Any]

@router.post("/put")
def put_item(body: PutItem):
    _store[body.key] = body.value
    return {"ok": True}

@router.get("/get")
def get_item(key: str):
    return {"key": key, "value": _store.get(key)}

@router.post("/events/append")
def append_event(body: AppendEvent):
    body.event.setdefault("ts", time.time())
    _events.setdefault(body.key, []).append(body.event)
    return {"ok": True}

@router.get("/events")
def list_events(key: str, limit: int = 50):
    return {"key": key, "events": _events.get(key, [])[-limit:]}
