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


EXAMPLES = '''
User: "What is the return policy?"
Output:
{
    "intent": "POLICY",
    "confidence": 0.95,
    "reason": "Asks directly about return policy"
}

User: "Can I return a damaged item?"
Output:
{
    "intent": "POLICY",
    "confidence": 0.9,
    "reason": "Asks about eligibility to return a damaged item"
}

User: "I want a refund for my order ORD123"
Output:
{
    "intent": "REFUND",
    "confidence": 0.98,
    "reason": "Explicit refund request with order id"
}

User: "Where is my order ORD999?"
Output:
{
    "intent": "ORDER_STATUS",
    "confidence": 0.96,
    "reason": "Asks for order status/tracking"
}

User: "My package is late and I'm angry"
Output:
{
    "intent": "ORDER_STATUS",
    "confidence": 0.8,
    "reason": "Mentions order delay and asks about status (escalation handled elsewhere)"
}

User: "This service is terrible"
Output:
{
    "intent": "OTHER",
    "confidence": 0.75,
    "reason": "Complaint but no specific order or refund request"
}

User: "Hello"
Output:
{
    "intent": "OTHER",
    "confidence": 0.6,
    "reason": "Greeting"
}
'''


def classify_intent_llm(query: str) -> IntentResult:
    llm = get_llm()

    # Provide the system prompt plus a few-shot examples to the model
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": EXAMPLES},
        {"role": "user", "content": query},
    ]

    response = llm.invoke(messages)

    def _extract_json(text: str):
        import json, re

        # Try direct parse first
        try:
            return json.loads(text)
        except Exception:
            pass

        # Fallback: extract the first {...} block
        m = re.search(r"(\{.*\})", text, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except Exception:
                return None
        return None

    data = _extract_json(response.content)
    if data:
        try:
            return IntentResult(**data)
        except Exception:
            pass

    # Fallback for safety
    # If parsing failed, use a simple keyword-based heuristic as a final fallback
    q = query.lower()
    if "refund" in q or "money back" in q:
        return IntentResult(intent=IntentLabel.REFUND, confidence=0.8, reason="Keyword match: refund")
    if "return" in q or "return policy" in q:
        return IntentResult(intent=IntentLabel.POLICY, confidence=0.75, reason="Keyword match: return")
    if "order" in q or "track" in q or "where is my" in q:
        return IntentResult(intent=IntentLabel.ORDER_STATUS, confidence=0.7, reason="Keyword match: order status")

    return IntentResult(
        intent=IntentLabel.OTHER,
        confidence=0.3,
        reason="Failed to parse LLM output",
    )
