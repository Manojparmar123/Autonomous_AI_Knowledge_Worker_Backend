from pydantic import BaseModel
from typing import Optional, List, Any

class IngestRequest(BaseModel):
    source: str  # newsapi|alphavantage|google|upload
    query: Optional[str] = None
    params: Optional[dict] = None

class RunResponse(BaseModel):
    task_id: str

class InsightModel(BaseModel):
    type: str
    text: str
    confidence: float
    topics: List[str] = []
    evidence: List[dict] = []
