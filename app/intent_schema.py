from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class IntentLabel(str, Enum):
    POLICY = "POLICY"
    ORDER_STATUS = "ORDER_STATUS"
    REFUND = "REFUND"
    OTHER = "OTHER"


class IntentResult(BaseModel):
    intent: IntentLabel = Field(..., description="Predicted user intent")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str = Field(..., description="Why this intent was chosen")

class MultiIntentResult(BaseModel):
    intents: List[IntentResult]
    chosen_intent: IntentLabel
    reason: str
    