from pathlib import Path
import ollama

from app.llm import get_llm
from app.config import OLLAMA_MODEL
from app.rag.chroma_client import get_collection

# Load persistent Chroma DB via centralized helper
collection = get_collection("policies")


def retrieve_context(query: str, k: int = 3) -> str:
    """
    Retrieve top-k relevant chunks from Chroma
    """
    # Compute query embedding via Ollama to avoid Chroma's default ONNX download
    try:
        q_emb = ollama.embeddings(model=OLLAMA_MODEL, prompt=query)["embedding"]
        results = collection.query(
            query_embeddings=[q_emb],
            n_results=k,
        )
        documents = results["documents"][0]
    except Exception:
        # Fallback to text-based query (may trigger ONNX download)
        results = collection.query(
            query_texts=[query],
            n_results=k,
        )
        documents = results["documents"][0]

    context = "\n\n".join(documents)
    return context


def answer_question(query: str) -> dict:
    """
    Generate a grounded answer using retrieved context
    """
    context = retrieve_context(query)

    prompt = f"""
You are a customer support assistant.

RULES (must follow strictly):
- Answer ONLY using the context below.
- Do NOT add general knowledge.
- Do NOT add explanations.
- Do NOT add suggestions.
- If the context does not fully answer the question, reply with EXACTLY:
"I don't have enough information to answer that."
- Do not say anything else after that sentence.

Context:
{context}

Question:
{query}
"""

    llm = get_llm()
    response = llm.invoke(prompt)

    return {
        "question": query,
        "answer": response.content,
        "sources": context,
    }

def is_weak_answer(answer: str) -> bool:
    refusal_phrases = [
        "I don't have enough information",
        "I'm not sure",
        "cannot determine",
        "insufficient information",
    ]
    return any(p.lower() in answer.lower() for p in refusal_phrases)
