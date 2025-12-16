import re

from app.intent_classifier import classify_intent
from app.intent import Intent
from app.rag.rag_answer import answer_question
from app.tools.order_lookup import lookup_order


def route_query(query: str) -> dict:
    intent = classify_intent(query)

    if intent == Intent.POLICY:
        return {
            "intent": intent,
            "result": answer_question(query),
        }

    elif intent == Intent.ORDER_STATUS:
        # naive order id extraction for now
        match = re.search(r"(ORD\d+)", query)
        order_id = match.group(1) if match else None

        if not order_id:
            return {
                "intent": intent,
                "result": "Please provide your order ID.",
            }

        return {
            "intent": intent,
            "result": lookup_order(order_id),
        }

    else:
        return {
            "intent": intent,
            "result": "I can help with order status or return policies.",
        }
