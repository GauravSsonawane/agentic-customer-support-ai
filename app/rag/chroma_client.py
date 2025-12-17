from pathlib import Path
import threading

# Centralized Chroma client helper for the project
CHROMA_DIR = Path("data/embeddings").resolve()
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


# Try to import chromadb; if unavailable, provide a lightweight in-memory
# fallback so the app can run without the dependency (useful for CI or dev).
try:
    import chromadb

    _HAS_CHROMADB = True
except Exception:
    chromadb = None  # type: ignore[assignment]
    _HAS_CHROMADB = False


# Use a simple module-level cache to reuse the same client across imports
_CLIENT = None
_CLIENT_LOCK = threading.Lock()


if _HAS_CHROMADB:
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

else:
    # Minimal in-memory fallback mimicking the Chroma API surface used in this project
    class _InMemoryCollection:
        def __init__(self, name: str):
            self.name = name
            self._documents = []
            self._metadatas = []
            self._embeddings = []
            self._ids = []

        def add(self, *, documents=None, metadatas=None, embeddings=None, ids=None, **kwargs):
            documents = documents or []
            metadatas = metadatas or [None] * len(documents)
            embeddings = embeddings or [None] * len(documents)
            ids = ids or [None] * len(documents)
            for d, m, e, i in zip(documents, metadatas, embeddings, ids):
                self._documents.append(d)
                self._metadatas.append(m)
                self._embeddings.append(e)
                self._ids.append(i)

        def count(self):
            return len(self._documents)

        def peek(self, limit: int = 5):
            return {"documents": self._documents[:limit]}

        def query(self, *, query_embeddings=None, query_texts=None, n_results=3, **kwargs):
            # naive similarity: return first n_results documents
            docs = self._documents[:n_results]
            return {"documents": [docs], "metadatas": [self._metadatas[:n_results]]}


    class _InMemoryClient:
        def __init__(self):
            self._collections = {}

        def get_or_create_collection(self, name: str):
            if name not in self._collections:
                self._collections[name] = _InMemoryCollection(name)
            return self._collections[name]

        def persist(self):
            return None


    _IN_MEMORY_CLIENT = _InMemoryClient()


    def get_client():
        return _IN_MEMORY_CLIENT


    def get_collection(name: str):
        return _IN_MEMORY_CLIENT.get_or_create_collection(name)


    def persist():
        return None
