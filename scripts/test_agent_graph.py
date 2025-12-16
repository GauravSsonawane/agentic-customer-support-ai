import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.agent_graph import build_graph


graph = build_graph()

queries = [
    "What is the return policy?",
    "Where is my order ORD123?",
    "I am very angry, this service is terrible",
]

for q in queries:
    print("\nQUERY:", q)
    result = graph.invoke(
        {
            "query": q,
            "intent": None,
            "response": None,
            "escalate": False,
        }
    )
    print("RESPONSE:", result.get("response"))


