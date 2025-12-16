import sys
from pathlib import Path

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from app.llm import get_llm

llm = get_llm()
response = llm.invoke("Say hello in one sentence.")

print(response.content)
