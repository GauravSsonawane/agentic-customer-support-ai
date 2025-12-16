from pathlib import Path
import sys
import ollama

# Ensure project root is on sys.path so `app` imports work when running the script
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.rag.chroma_client import get_collection

# IMPORTANT: use centralized helper for collection
collection = get_collection("policies")


def embed_query(query, model="llama3.1"):
    response = ollama.embeddings(model=model, prompt=query)
    return response["embedding"]


query = "What is the return policy?"

query_embedding = embed_query(query)

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3,
)

print("Top retrieved chunks:\n")

for doc in results.get("documents", [[]])[0]:
    print("----")
    print((doc or "")[:300])
