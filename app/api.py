from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from starlette.concurrency import run_in_threadpool

from app.agent_graph import build_graph

# ---------------------------------
# FastAPI app
# ---------------------------------
app = FastAPI(title="Agentic Customer Support API")

# Build graph ONCE (important)
graph = build_graph()

# ---------------------------------
# Request / Response models
# ---------------------------------
class QueryRequest(BaseModel):
    query: str
    thread_id: str


class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool = True


# ---------------------------------
# Start agent execution
# ---------------------------------
@app.post("/query")
async def run_agent(req: QueryRequest):
    state = {
        "query": req.query,
        "intent": None,
        "response": None,
        "escalate": False,
        "thread_id": req.thread_id,
    }

    # LangGraph is sync → run in threadpool
    result = await run_in_threadpool(
        graph.invoke,
        state,
        {"configurable": {"thread_id": req.thread_id}},
    )

    return result


# ---------------------------------
# Resume after Human-in-the-Loop
# ---------------------------------
@app.post("/query/resume")
async def resume_agent(req: ResumeRequest):
    # Resume execution with approval decision
    result = await run_in_threadpool(
        graph.resume,
        None,                # interrupt_id auto-resolved by thread_id
        req.approved,
        {"configurable": {"thread_id": req.thread_id}},
    )

    return result

