import asyncio
import logging
import ollama

from app.llm import get_llm
from app.config import OLLAMA_MODEL
from app.rag.chroma_client import get_collection

logger = logging.getLogger(__name__)

# Persistent Chroma collection
collection = get_collection("policies")


# ------------------------------------------------
# ASYNC: Retrieve context from Chroma
# ------------------------------------------------
async def retrieve_context_async(query: str, k: int = 5) -> str:
    """
    Async wrapper around embedding + Chroma query.
    Runs blocking IO in a thread executor.
    """
    loop = asyncio.get_running_loop()

    def _embed_and_query():
        try:
            # Compute embedding via Ollama
            embedding = ollama.embeddings(
                model=OLLAMA_MODEL,
                prompt=query,
           )["embedding"]

            results = collection.query(
                query_embeddings=[embedding],
                n_results=k,
            )

            # Log a compact preview of retrieved chunks for debugging
            docs = results.get("documents", [[]])[0]
            logger.debug("Retrieved %d chunks for query", len(docs))
            for d in docs:
                preview = (d[:120] + "...") if len(d) > 120 else d
                logger.debug("- %s", preview.replace("\n", " "))

            return "\n\n".join(docs)
        except Exception as e:
            logger.exception("Error during embedding or Chroma query")
            # Return empty context so downstream code can handle gracefully
            return ""

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
- If the context is related but does not give a complete answer,
  provide the best possible answer strictly from the context.
- ONLY if the context is completely unrelated, reply with EXACTLY:
  "I don't have enough information to answer that question."

Context:
{context}

Question:
{query}
"""

    llm = get_llm()
    loop = asyncio.get_running_loop()

    try:
        response = await loop.run_in_executor(
            None,
            lambda: llm.invoke(prompt)
        )

        answer = response.content.strip()

        return {
            "question": query,
            "answer": answer,
            "sources": context,
            "is_weak": is_weak_answer(answer),
        }
    except Exception:
        logger.exception("LLM invocation failed for query: %s", query)
        return {
            "question": query,
            "answer": "",
            "sources": context,
            "is_weak": True,
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
    """
    Returns True ONLY when the model explicitly refuses
    or produces an empty response.
    """
    if not answer or not answer.strip():
        return True

    refusal_phrases = [
        "i don't have enough information",
        "i am not sure",
        "i'm not sure",
        "cannot determine",
        "insufficient information",
    ]

    answer_lower = answer.lower()
    return any(p in answer_lower for p in refusal_phrases)
