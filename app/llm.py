from langchain_ollama import ChatOllama
from app.config import OLLAMA_MODEL, OLLAMA_BASE_URL, TEMPERATURE

def get_llm():
    return ChatOllama(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=TEMPERATURE,
    )
