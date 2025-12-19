from fastapi import APIRouter

from app.router import route_query

router = APIRouter()

@router.get("/chat")
def chat():
    return {"message": "Chat endpoint placeholder"}


@router.post("/query")
def query(payload: dict):
    query_text = payload.get("query")
    thread_id = payload.get("thread_id")

    if not query_text:
        return {
            "final_answer": "No query provided.",
            "decision": "invalid_request",
            "escalate": False,
        }

    result = route_query(query_text)
    result["thread_id"] = thread_id
    return result



