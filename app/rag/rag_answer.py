import asyncio
import ollama

from app.llm import get_llm
from app.config import OLLAMA_MODEL
from app.rag.chroma_client import get_collection

# Persistent Chroma collection
collection = get_collection("policies")


# ------------------------------------------------
# ASYNC: Retrieve context from Chroma
# ------------------------------------------------
async def retrieve_context_async(query: str, k: int = 3) -> str:
    """
    Async wrapper around embedding + Chroma query.
    Runs blocking IO in a thread executor.
    """
    loop = asyncio.get_running_loop()

    def _embed_and_query():
        # Compute embedding via Ollama
        embedding = ollama.embeddings(
            model=OLLAMA_MODEL,
            prompt=query,
        )["embedding"]

        results = collection.query(
            query_embeddings=[embedding],
            n_results=k,
        )

        return "\n\n".join(results["documents"][0])

    return await loop.run_in_executor(None, _embed_and_query)


# ------------------------------------------------
# ASYNC: Generate grounded answer
# ------------------------------------------------
async def answer_question_async(query: str) -> dict:
    context = await retrieve_context_async(query)

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
    loop = asyncio.get_running_loop()

    response = await loop.run_in_executor(
        None,
        lambda: llm.invoke(prompt)
    )

    return {
        "question": query,
        "answer": response.content,
        "sources": context,
    }


# ------------------------------------------------
# SYNC WRAPPER (Backwards compatible)
# ------------------------------------------------
def answer_question(query: str) -> dict:
    """
    Sync wrapper so existing code does NOT break.
    """
    return asyncio.run(answer_question_async(query))


# ------------------------------------------------
# Confidence helper (unchanged)
# ------------------------------------------------
def is_weak_answer(answer: str) -> bool:
    refusal_phrases = [
        "i don't have enough information",
        "i'm not sure",
        "cannot determine",
        "insufficient information",
    ]
    return any(p in answer.lower() for p in refusal_phrases)
