import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.rag.rag_answer import answer_question


query = "What is the return policy?"

result = answer_question(query)

print("\nQUESTION:")
print(result["question"])

print("\nANSWER:")
print(result["answer"])

print("\nSOURCE CONTEXT:")
print(result["sources"][:500])
