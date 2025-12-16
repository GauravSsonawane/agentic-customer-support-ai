from app.intent_classifier import classify_intent
from app.intent import Intent
from app.rag.rag_answer import answer_question
from app.tools.order_lookup import lookup_order
from app.llm import get_llm
import re


def analyze_node(state):
    query = state["query"]

    intent = classify_intent(query)

    # crude sentiment check (we’ll improve later)
    angry_words = ["angry", "frustrated", "useless", "terrible"]
    escalate = any(w in query.lower() for w in angry_words)

    return {
        **state,
        "intent": intent,
        "escalate": escalate,
    }


def policy_node(state):
    result = answer_question(state["query"])
    return {
        **state,
        "response": result["answer"],
    }


def order_node(state):
    match = re.search(r"(ORD\d+)", state["query"])
    order_id = match.group(1) if match else None

    if not order_id:
        response = "Please provide your order ID."
    else:
        response = lookup_order(order_id)

    return {
        **state,
        "response": response,
    }


def escalation_node(state):
    return {
        **state,
        "response": "This issue has been escalated to a human support agent.",
    }

