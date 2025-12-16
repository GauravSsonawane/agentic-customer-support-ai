from pathlib import Path
import chromadb
import ollama

# Always resolve absolute path (Windows-safe)
CHROMA_DIR = Path("data/embeddings").resolve()

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

# IMPORTANT: use get_or_create_collection
collection = client.get_or_create_collection("policies")


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

for doc in results["documents"][0]:
    print("----")
    print(doc[:300])
