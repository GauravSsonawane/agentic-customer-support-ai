import sys
from unittest.mock import MagicMock

# Mock heavy/external dependencies to allow health check to pass without full env
sys.modules["ollama"] = MagicMock()
sys.modules["langgraph"] = MagicMock()
sys.modules["langgraph.graph"] = MagicMock()
sys.modules["langsmith"] = MagicMock()
sys.modules["chromadb"] = MagicMock()


import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
