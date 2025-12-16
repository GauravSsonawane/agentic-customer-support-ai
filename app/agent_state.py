from typing import TypedDict, Optional
from app.intent import Intent


class AgentState(TypedDict):
    query: str
    intent: Optional[Intent]
    response: Optional[str]
    escalate: bool

