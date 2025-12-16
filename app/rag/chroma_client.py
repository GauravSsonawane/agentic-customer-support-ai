from pathlib import Path
import threading
import chromadb

# Centralized Chroma client helper for the project
CHROMA_DIR = Path("data/embeddings").resolve()
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Use a simple module-level cache to reuse the same client across imports
_CLIENT = None
_CLIENT_LOCK = threading.Lock()


def get_client() -> chromadb.PersistentClient:
    global _CLIENT
    if _CLIENT is None:
        with _CLIENT_LOCK:
            if _CLIENT is None:
                _CLIENT = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _CLIENT


def get_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(name)


def persist():
    try:
        get_client().persist()
    except Exception:
        pass
