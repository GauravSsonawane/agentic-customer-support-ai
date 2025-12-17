import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.agent_graph import build_graph
from langgraph.types import Command

graph = build_graph()

thread_id = "refund-thread-001"

# STEP 1: Start execution (will interrupt)
state = {
    "query": "I want a refund for my order ORD123",
    "intent": None,
    "response": None,
    "escalate": False,
}

print("\n=== FIRST RUN (will interrupt) ===\n")

result = graph.invoke(
    state,
    config={"configurable": {"thread_id": thread_id}},
)

print("INTERRUPTED STATE:", result)

interrupt_id = result["__interrupt__"][0].id

print("\n--- Simulating process restart ---\n")

# STEP 2: "Restart" app (new graph instance)
graph = build_graph()

print("\nADMIN: approving refund after restart...\n")

# STEP 3: Resume after restart using the Command(resume=...) pattern.
# `graph.stream(...)` yields execution chunks; the resume value is provided
# as the `resume` field of a `Command`.
result = None
for chunk in graph.stream(Command(resume=True), config={"configurable": {"thread_id": thread_id}}):
    print("STREAM CHUNK:", chunk)
    result = chunk

print("\nFINAL CHUNK:", result)
