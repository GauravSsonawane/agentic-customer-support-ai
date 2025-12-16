from pathlib import Path
import sys

# Ensure project root is on sys.path so `app` imports work when running the script
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.rag.chroma_client import get_collection

# Use centralized helper to get the collection
collection = get_collection("policies")

print("Document count:", collection.count())

print("\nPeeking stored documents:\n")
peek = collection.peek(limit=5)

for doc in peek.get("documents", []):
    print("----")
    print((doc or "")[:200])