import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))
ESCALATION_SENTIMENT = os.getenv("ESCALATION_SENTIMENT", "angry")


