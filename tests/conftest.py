"""
Configuração global dos testes.

Define variáveis de ambiente ANTES de qualquer import do app,
garantindo que o Settings do pydantic-settings leia os valores corretos.

Estratégia de CI:
  - RETRIEVAL_METHOD=tfidf  → usa scikit-learn (leve, sem FAISS/sentence-transformers)
  - LLM_PROVIDER vazio      → testes não chamam LLM real
  - RATE_LIMIT_ENABLED=false → sem rate limit nos testes
  - AGENT_ENABLED=false     → não inicia o agent
"""
import os

os.environ.setdefault("RETRIEVAL_METHOD", "tfidf")
os.environ.setdefault("LLM_PROVIDER", "openrouter")
os.environ.setdefault("OPENROUTER_API_KEY", "")
os.environ.setdefault("AZURE_OPENAI_KEY", "")
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("AGENT_ENABLED", "false")

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """TestClient ASGI — sem servidor real, sem rede."""
    return TestClient(app)


@pytest.fixture(scope="session")
def escritorio_id() -> str:
    return "esc-pytest"
