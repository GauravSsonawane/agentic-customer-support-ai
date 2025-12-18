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


EXAMPLES = '''
User: "I want a refund for my order ORD123"
Output:
{
    "intents": [
        {"intent": "REFUND", "confidence": 0.98, "reason": "Explicit refund request with order id"}
    ]
}

User: "My package is late and I'm angry"
Output:
{
    "intents": [
        {"intent": "ORDER_STATUS", "confidence": 0.85, "reason": "Asks about order status/delay"},
        {"intent": "OTHER", "confidence": 0.5, "reason": "Expresses anger/complaint"}
    ]
}

User: "Can I return a damaged item?"
Output:
{
    "intents": [
        {"intent": "POLICY", "confidence": 0.92, "reason": "Asks about return eligibility for damaged item"}
    ]
}
'''


def classify_multi_intent(query: str) -> MultiIntentResult:
    llm = get_llm()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": EXAMPLES},
        {"role": "user", "content": query},
    ]

    response = llm.invoke(messages)

    def _extract_json(text: str):
        import json, re

        try:
            return json.loads(text)
        except Exception:
            pass

        m = re.search(r"(\{.*\})", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None

    data = _extract_json(response.content)
    if data and "intents" in data:
        try:
            intents = [IntentResult(**i) for i in data["intents"]]
        except Exception:
            intents = None
    else:
        intents = None

    if not intents:
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
