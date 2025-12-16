from pathlib import Path
import chromadb

CHROMA_DIR = Path("data/embeddings").resolve()
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_collection("policies")

print("Document count:", collection.count())
