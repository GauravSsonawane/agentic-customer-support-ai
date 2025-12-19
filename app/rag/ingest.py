from pathlib import Path
import sys
from pypdf import PdfReader

# Ensure project root is on sys.path when running this file directly
# so `from app...` imports work (allows `python app/rag/ingest.py`).
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import ollama

from app.rag.chroma_client import get_collection, persist


DATA_DIR = Path("data/policies")


def load_pdfs():
    documents = []

    for pdf_path in DATA_DIR.glob("*.pdf"):
        reader = PdfReader(pdf_path)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": pdf_path.name,
                        "page": page_num,
                    }
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
        chunk_size=400,
        chunk_overlap=60,
        separators=[
            "\n\n",   # paragraphs / sections
            "\n",     # line breaks
            ".",      # sentences
            " ",      # words (last resort)
        ],
    )

    chunks = splitter.split_documents(docs)



    collection = get_collection("policies")

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
    persist()

    print(f"Ingested {len(texts)} chunks into ChromaDB")


if __name__ == "__main__":
    ingest()


