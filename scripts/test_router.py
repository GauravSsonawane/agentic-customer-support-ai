import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.router import route_query


queries = [
    "What is the return policy?",
    "Where is my order ORD123?",
    "Hello there",
]

for q in queries:
    print("\nQUERY:", q)
    response = route_query(q)
    print("INTENT:", response["intent"])
    print("RESULT:", response["result"])
