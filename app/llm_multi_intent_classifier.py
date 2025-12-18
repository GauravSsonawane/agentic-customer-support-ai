from app.llm import get_llm
from app.intent_schema import IntentResult, MultiIntentResult, IntentLabel
from app.intent_priority import INTENT_PRIORITY
import json


SYSTEM_PROMPT = """
You are an intent detection system for customer support.

Identify ALL relevant intents in the user query.
Possible intents:
- POLICY
- ORDER_STATUS
- REFUND
- OTHER

Return ONLY valid JSON in this format:

{
  "intents": [
    {"intent": "<INTENT>", "confidence": <0-1>, "reason": "<why>"}
  ]
}

Rules:
- Include ALL applicable intents
- Assign higher confidence to more explicit requests
"""


def classify_multi_intent(query: str) -> MultiIntentResult:
    llm = get_llm()

    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
    )

    try:
        data = json.loads(response.content)
        intents = [IntentResult(**i) for i in data["intents"]]

    except Exception:
        intents = [
            IntentResult(
                intent=IntentLabel.OTHER,
                confidence=0.3,
                reason="Failed to parse LLM output",
            )
        ]

    # 🔥 Prioritization logic
    intents_sorted = sorted(
        intents,
        key=lambda i: (INTENT_PRIORITY[i.intent], i.confidence),
        reverse=True,
    )

    chosen = intents_sorted[0]

    return MultiIntentResult(
        intents=intents,
        chosen_intent=chosen.intent,
        reason=f"Chosen based on priority ({INTENT_PRIORITY[chosen.intent]}) and confidence ({chosen.confidence})",
    )
