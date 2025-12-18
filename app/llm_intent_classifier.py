from app.llm import get_llm
from app.intent_schema import IntentResult, IntentLabel
import json


SYSTEM_PROMPT = """
You are an intent classification system for a customer support agent.

Your job is to classify the user's intent into one of:
- POLICY
- ORDER_STATUS
- REFUND
- OTHER

Return ONLY valid JSON in this exact format:

{
  "intent": "<INTENT>",
  "confidence": <number between 0 and 1>,
  "reason": "<short explanation>"
}

Rules:
- POLICY: questions about returns, policies, eligibility
- ORDER_STATUS: tracking or order status queries
- REFUND: explicit refund or money-back requests
- OTHER: greetings or irrelevant messages
"""


def classify_intent_llm(query: str) -> IntentResult:
    llm = get_llm()

    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    try:
        data = json.loads(response.content)
        return IntentResult(**data)
    except Exception:
        # Fallback for safety
        return IntentResult(
            intent=IntentLabel.OTHER,
            confidence=0.3,
            reason="Failed to parse LLM output",
        )
