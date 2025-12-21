from fastapi import APIRouter

from app.router import route_query
from app.state.checkpointer import SQLiteCheckpointer

router = APIRouter()

# ✅ Create checkpointer ONCE at module level
checkpointer = SQLiteCheckpointer()


@router.get("/chat")
def chat():
    return {"message": "Chat endpoint placeholder"}


@router.post("/query")
def query(payload: dict):
    query_text = payload.get("query")
    thread_id = payload.get("thread_id")

    if not query_text or not thread_id:
        return {
            "final_answer": "Missing query or thread_id.",
            "decision": "invalid_request",
            "escalate": False,
        }

    # --------------------------------------------------
    # 1️⃣ LOAD STATE (or initialize)
    # --------------------------------------------------
    state = checkpointer.load(thread_id) or {
        "thread_id": thread_id,
        "messages": [],
        "last_intent": None,
        "last_decision": None,
        "pending_clarification": False,
        "clarification_type": None,
        "clarification_question": None,
        "pending_human": False,
    }

    # --------------------------------------------------
    # 2️⃣ STORE USER MESSAGE
    # --------------------------------------------------
    state["messages"].append({
        "role": "user",
        "content": query_text
    })

    # --------------------------------------------------
    # 3️⃣ RUN AGENT LOGIC (resume clarification if needed)
    # Wrap routing in try/except so errors are returned as structured responses
    # instead of raising uncaught exceptions that crash the request handler.
    # --------------------------------------------------
    try:
        if state.get("pending_clarification") and state.get("clarification_question"):
            combined_query = (
                f"{state['clarification_question']} "
                f"The item details are: {query_text}"
            )
            result = route_query(combined_query)
        else:
            result = route_query(query_text)
    except Exception as e:
        # Keep a minimal, UI-friendly response shape and log the error server-side.
        # The UI will show a generic error but we keep logs for debugging.
        import logging
        logging.exception("Error while routing query: %s", query_text)

        return {
            "final_answer": "An internal error occurred while processing the request.",
            "intent": None,
            "confidence": 0.0,
            "decision": "internal_error",
            "sources": None,
            "escalate": False,
            "error": str(e),
            "thread_id": thread_id,
        }

    # --------------------------------------------------
    # 4️⃣ UPDATE CLARIFICATION STATE
    # --------------------------------------------------
    if result.get("decision") in [
        "policy_needs_clarification",
        "refund_policy_needs_clarification",
    ]:
        state["pending_clarification"] = True
        state["clarification_type"] = "return_item_details"

        # ✅ Store ORIGINAL question only once
        if not state.get("clarification_question"):
            state["clarification_question"] = query_text

    else:
        state["pending_clarification"] = False
        state["clarification_type"] = None
        state["clarification_question"] = None

    # --------------------------------------------------
    # 5️⃣ STORE ASSISTANT MESSAGE
    # --------------------------------------------------
    state["messages"].append({
        "role": "assistant",
        "content": result.get("final_answer")
    })

    state["last_intent"] = str(result.get("intent"))
    state["last_decision"] = result.get("decision")

    # 🚫 Do NOT escalate while clarification is pending
    state["pending_human"] = (
        False if state["pending_clarification"]
        else result.get("escalate", False)
    )

    # --------------------------------------------------
    # 6️⃣ SAVE STATE
    # --------------------------------------------------
    checkpointer.save(thread_id, state)

    # --------------------------------------------------
    # 7️⃣ RETURN RESPONSE
    # --------------------------------------------------
    result["thread_id"] = thread_id
    return result
