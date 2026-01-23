from typing import Any, Optional

from pydantic import BaseModel


class QueryRequest(BaseModel):
    query: str
    thread_id: str


class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool = True


class QueryResponse(BaseModel):
    final_answer: Optional[str] = None
    intent: Optional[Any] = None
    confidence: Optional[float] = None
    decision: Optional[str] = None
    sources: Optional[Any] = None
    escalate: bool = False
    error: Optional[str] = None
    thread_id: str
