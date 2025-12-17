from langgraph.graph import StateGraph, END
from app.agent_state import AgentState
from app.agent_nodes import (
    analyze_node,
    policy_node,
    order_node,
    escalation_node,
    refund_node,
)
from app.intent import Intent


def route_from_analyze(state):
    if state["escalate"]:
        return "escalate"

    if state["intent"] == Intent.REFUND:
            return "refund"

    if state["intent"] == Intent.POLICY:
        return "policy"

    if state["intent"] == Intent.ORDER_STATUS:
        return "order"

    return END


def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", analyze_node)
    workflow.add_node("policy", policy_node)
    workflow.add_node("order", order_node)
    workflow.add_node("escalate", escalation_node)
    workflow.add_node("refund", refund_node)

    workflow.set_entry_point("analyze")

    workflow.add_conditional_edges(
        "analyze",
        route_from_analyze
    )

    workflow.add_edge("policy", END)
    workflow.add_edge("order", END)
    workflow.add_edge("escalate", END)
    workflow.add_edge("refund", END)

    return workflow.compile()
