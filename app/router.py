from app.intent_schema import IntentLabel
from app.intent_classifier import classify_intent
from app.rag.rag_answer import answer_question
from app.tools.order_lookup import lookup_order
from app.rag.rag_answer import answer_question, is_weak_answer

def route_query(query: str) -> dict:
    intent_result = classify_intent(query)

    intent = intent_result.intent
    confidence = intent_result.confidence

    if intent == IntentLabel.POLICY:

        rag_result = answer_question(query)
        answer = rag_result["answer"]

        if is_weak_answer(answer):
            return {
            "intent": intent_result,
            "result": (
                "I found some relevant policy information, but I’m not confident "
                "enough to give a precise answer. Would you like me to escalate this "
                "to a human agent?"
            ),
            "sources": rag_result["sources"],
            "confidence": 0.3,
            "decision": "refused_low_confidence",
        }

        return {
            "intent": intent_result,
            "result": rag_result["answer"],
            "sources": rag_result["sources"],
            "confidence": 0.9,
            "decision": "answered_from_policy",
            }


    elif intent == IntentLabel.ORDER_STATUS:
        order_id = next((w for w in query.split() if w.startswith("ORD")), None)

        if not order_id:
            return {
                "intent": intent_result,
                "result": "Please provide your order ID.",
            }

        return {
            "intent": intent_result,
            "result": lookup_order(order_id),
        }

    elif intent == IntentLabel.REFUND:
        return {
            "intent": intent_result,
            "result": "Refund request requires approval.",
        }

    else:
        return {
            "intent": intent_result,
            "result": "I can help with order status or return policies.",
        }
