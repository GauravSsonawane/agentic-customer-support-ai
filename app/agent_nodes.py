import re

from langgraph.types import interrupt

from app.agent_logger import log_step


from app.intent_classifier import classify_intent
from app.intent import Intent
from app.rag.rag_answer import answer_question
from app.tools.order_lookup import lookup_order
from app.llm import get_llm



def analyze_node(state):
    log_step("analyze", state)
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
    log_step("policy", state)
    result = answer_question(state["query"])
    return {
        **state,
        "response": result["answer"],
    }


def order_node(state):
    log_step("order", state)
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
    log_step("escalation", state)
    return {
        **state,
        "response": "This issue has been escalated to a human support agent.",
    }


def refund_node(state):
    log_step("refund_request", state)
    # Pause execution and wait for human approval using the langgraph helper.
    # `interrupt` will raise the appropriate GraphInterrupt on first call
    # and return the resume value when the graph is resumed.
    approval = interrupt("⚠ Refund requested. Awaiting admin approval.")

    # This part runs ONLY after resume; expect `approval` to be truthy when approved
    if approval or state.get("approved"):
        return {
            **state,
            "response": "Refund approved. It will be processed shortly.",
        }
    else:
        return {
            **state,
            "response": "Refund request denied.",
        }

