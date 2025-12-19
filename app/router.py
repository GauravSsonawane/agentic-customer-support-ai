# from app.intent_schema import IntentLabel
# from app.intent_classifier import classify_intent
# from app.tools.order_lookup import lookup_order
# from app.rag.rag_answer import answer_question, is_weak_answer

# def route_query(query: str) -> dict:
#     """
#     Clean, confidence-aware router.
#     Returns a unified response schema for UI + API.
#     """

#     intent_result = classify_intent(query)

#     intent = intent_result.intent
#     confidence = intent_result.confidence
#     reason = intent_result.reason

#     ## Policy Questions

#     if intent == IntentLabel.POLICY:

#         rag_result = answer_question(query)
#         answer = rag_result["answer"]

#         if is_weak_answer(answer):
#             return {
#             "final_answer": (
#                 "I found some relevant policy information, but I’m not confident "
#                 "enough to give a precise answer. Would you like me to escalate this "
#                 "to a human agent?"
#             ),
#             "intent": intent_result,
#             "sources": rag_result["sources"],
#             "confidence": 0.4,
#             "decision": "policy_low_confidence",
#         }
    
#         return {
#             "final_answer": answer,
#             "intent": intent_result,
#             "confidence": 0.9,
#             "decision": "policy_answered",
#             "sources": rag_result["sources"],
#         }

#     ## Order Status

#     if intent == IntentLabel.ORDER_STATUS:
#         order_id = next((w for w in query.split() if w.startswith("ORD")), None)

#         if not order_id:
#             return {
#                 "intent": intent_result,
#                 "result": "Please provide your order ID.",
#             }

#         return {
#             "intent": intent_result,
#             "result": lookup_order(order_id),
#         }

#     elif intent == IntentLabel.REFUND:
#         return {
#             "intent": intent_result,
#             "result": "Refund request requires approval.",
#         }

#     else:
#         return {
#             "intent": intent_result,
#             "result": "I can help with order status or return policies.",
#         }

from app.intent_schema import IntentLabel
from app.intent_classifier import classify_intent
from app.rag.rag_answer import answer_question, is_weak_answer
from app.tools.order_lookup import lookup_order


def route_query(query: str) -> dict:
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

        # Low-confidence or incomplete policy answer
        if is_weak_answer(answer):
            return {
                "final_answer": (
                    "I found some relevant policy information, but I’m not confident "
                    "enough to give a precise answer. Would you like me to escalate "
                    "this to a human support agent?"
                ),
                "intent": intent_result,
                "confidence": 0.4,
                "decision": "policy_low_confidence",
                "sources": rag_result["sources"],
            }

        # Strong policy answer
        return {
            "final_answer": answer,
            "intent": intent_result,
            "confidence": 0.9,
            "decision": "policy_answered",
            "sources": rag_result["sources"],
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
    # 3️⃣ REFUND REQUESTS (action-oriented only)
    # --------------------------------------------------
    if intent == IntentLabel.REFUND:

        # Refunds always require approval
        return {
            "final_answer": (
                "I understand you’re requesting a refund. "
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

