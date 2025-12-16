from pathlib import Path
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import chromadb
import ollama


DATA_DIR = Path("data/policies")
CHROMA_DIR = Path("data/embeddings").resolve()


def load_pdfs():
    documents = []

    for pdf_path in DATA_DIR.glob("*.pdf"):
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        documents.append(
            Document(
                page_content=text,
                metadata={"source": pdf_path.name}
            )
        )

    return documents


def embed_texts(texts, model="llama3.1"):
    embeddings = []
    for text in texts:
        response = ollama.embeddings(model=model, prompt=text)
        embeddings.append(response["embedding"])
    return embeddings


def ingest():
    docs = load_pdfs()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    chunks = splitter.split_documents(docs)

    # Ensure persistence directory exists and use PersistentClient for consistent access
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(name="policies")

    texts = [chunk.page_content for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    embeddings = embed_texts(texts)

    ids = [f"doc_{i}" for i in range(len(texts))]

    collection.add(
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
        ids=ids,
    )
    # Persist to disk (PersistentClient should handle this, but call persist() to be explicit)
    try:
        client.persist()
    except Exception:
        pass

    print(f"Ingested {len(texts)} chunks into ChromaDB")


if __name__ == "__main__":
    ingest()


