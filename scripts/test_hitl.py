import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.agent_graph import build_graph

graph = build_graph()

state = {
    "query": "I want a refund for my order ORD123",
    "intent": None,
    "response": None,
    "escalate": False,
}

result = graph.invoke(state)
print("\nINTERRUPTED:", result)

interrupts = result["__interrupt__"]
interrupt_id = interrupts[0].id

print("\nADMIN: approving refund...\n")

result = graph.invoke(
    state,
    config={
        "resume": {
            interrupt_id: True
        }
    }
)

print("\nFINAL RESPONSE:", result["response"])

