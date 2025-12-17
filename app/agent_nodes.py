import re
from app.observability import trace_event
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

    angry_phrases = [
        "angry", "frustrated", "terrible", "useless", "not happy", "worst"
    ]
    escalate = any(p in query.lower() for p in angry_phrases)

    trace_event(
        event_type="analyze",
        data={
            "query": query,
            "predicted_intent": intent.name,
            "escalate": escalate,
        },
        thread_id=state.get("thread_id", "default"),
    )

    return {
        **state,
        "intent": intent,
        "escalate": escalate,
    }


def policy_node(state):
    log_step("policy", state)

    result = answer_question(state["query"])

    trace_event(
        event_type="policy_rag",
        data={
            "query": state["query"],
            "answer_preview": result["answer"][:200],
        },
        thread_id=state.get("thread_id", "default"),
    )

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

    trace_event(
        event_type="refund_requested",
        data={"query": state["query"]},
        thread_id=state.get("thread_id", "default"),
    )

    approval = interrupt("⚠ Refund requested. Awaiting admin approval.")

    trace_event(
        event_type="refund_decision",
        data={"approved": bool(approval)},
        thread_id=state.get("thread_id", "default"),
    )

    if approval:
        return {
            **state,
            "response": "Refund approved. It will be processed shortly.",
        }
    else:
        return {
            **state,
            "response": "Refund request denied.",
        }


