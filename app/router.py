from langsmith import traceable

from app.intent_schema import IntentLabel
from app.intent_classifier import classify_intent
from app.rag.rag_answer import answer_question
from app.tools.order_lookup import lookup_order

def is_refund_question(query: str) -> bool:
    """
    Decide whether a refund-related query is a QUESTION (policy info)
    or an ACTION (initiate refund).
    """
    q = query.lower().strip()

    question_starters = [
        "can i",
        "can we",
        "am i",
        "is it",
        "do i",
        "what is",
        "how do",
        "how can",
        "does",
    ]

    action_phrases = [
        "i want",
        "i need",
        "process",
        "initiate",
        "request",
        "apply",
        "refund my",
        "give me a refund",
    ]

    # Explicit action → NOT a question
    if any(p in q for p in action_phrases):
        return False

    # Explicit question → question
    if any(q.startswith(p) for p in question_starters):
        return True

    # Default: treat ambiguous refund queries as questions first
    return True

@traceable(name="route_query")
def route_query(query: str, extra_context: str | None = None) -> dict:

    """
    Clean, confidence-aware router.
    Returns a unified response schema for UI + API.
    """

    intent_result = classify_intent(query)

    intent = intent_result.intent
    confidence = intent_result.confidence
    reason = intent_result.reason

    # --------------------------------------------------
    # 1️⃣ POLICY QUESTIONS (highest priority)
    # --------------------------------------------------
    if intent == IntentLabel.POLICY:

        rag_result = answer_question(query)

        answer = rag_result["answer"]
        is_weak = rag_result.get("is_weak", False)

        # Weak / conditional policy answer → clarification, NOT escalation
        if is_weak:
            return {
                "final_answer": (
                    f"{answer}\n\n"
                    "Could you please provide a bit more detail "
                    "(for example, product type or delivery date)?"
                ),
                "intent": intent_result,
                "confidence": 0.5,
                "decision": "policy_needs_clarification",
                "sources": rag_result["sources"],
                "escalate": False,
            }

        # Strong policy answer
        return {
            "final_answer": answer,
            "intent": intent_result,
            "confidence": 0.9,
            "decision": "policy_answered",
            "sources": rag_result["sources"],
            "escalate": False,
        }

    # --------------------------------------------------
    # 2️⃣ ORDER STATUS
    # --------------------------------------------------
    if intent == IntentLabel.ORDER_STATUS:

        order_id = next((w for w in query.split() if w.startswith("ORD")), None)

        if not order_id:
            return {
                "final_answer": "Please provide your order ID (e.g., ORD123).",
                "intent": intent_result,
                "confidence": confidence,
                "decision": "missing_order_id",
            }

        return {
            "final_answer": lookup_order(order_id),
            "intent": intent_result,
            "confidence": confidence,
            "decision": "order_lookup",
        }

# --------------------------------------------------
# 3️⃣ REFUND (question → policy first, action → escalate)
# --------------------------------------------------
    if intent == IntentLabel.REFUND:

        # 🟢 Refund-related QUESTION → try POLICY RAG first
        if is_refund_question(query):
            rag_result = answer_question(query)

            answer = rag_result["answer"]
            is_weak = rag_result.get("is_weak", False)

            # Strong policy answer → return it
            if answer and not is_weak:
                return {
                    "final_answer": answer,
                    "intent": intent_result,
                    "confidence": 0.85,
                    "decision": "refund_policy_answered",
                    "sources": rag_result.get("sources"),
                    "escalate": False,
                }

            # Weak / unclear policy answer → ask clarification
            return {
                "final_answer": (
                    "I can help with refund eligibility, but I need a bit more detail. "
                    "Is the item damaged, defective, or past the return window?"
                ),
                "intent": intent_result,
                "confidence": 0.5,
                "decision": "refund_policy_needs_clarification",
                "escalate": False,
            }

        # 🔴 True refund ACTION → escalate to human
        return {
            "final_answer": (
                "I understand you want to initiate a refund. "
                "This requires approval from a human support agent."
            ),
            "intent": intent_result,
            "confidence": confidence,
            "decision": "refund_requires_approval",
            "escalate": True,
        }


    # --------------------------------------------------
    # 4️⃣ OTHER / FALLBACK
    # --------------------------------------------------
    return {
        "final_answer": "I can help with return policies or order status. How can I assist you?",
        "intent": intent_result,
        "confidence": confidence,
        "decision": "fallback",
    }
