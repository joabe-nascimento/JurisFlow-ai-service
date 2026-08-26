"""
Testes de health check, status e verticais — não requerem LLM nem FAISS.
"""
from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200


def test_health_status_is_ok(client: TestClient):
    data = client.get("/health").json()
    assert data["status"] == "ok"
    assert "service" in data


def test_v1_status_returns_200(client: TestClient):
    r = client.get("/v1/status")
    assert r.status_code == 200


def test_v1_status_has_required_fields(client: TestClient):
    data = client.get("/v1/status").json()
    for field in ("service", "status", "llm_provider", "llm_model", "retrieval"):
        assert field in data, f"Campo ausente no /v1/status: {field}"


def test_v1_status_is_online(client: TestClient):
    assert client.get("/v1/status").json()["status"] == "online"


def test_v1_verticals_returns_200(client: TestClient):
    r = client.get("/v1/verticals")
    assert r.status_code == 200


def test_v1_verticals_has_current_vertical(client: TestClient):
    data = client.get("/v1/verticals").json()
    assert "current_vertical" in data
    assert "available_verticals" in data


def test_v1_usage_returns_200(client: TestClient):
    r = client.get("/v1/usage")
    assert r.status_code == 200


def test_v1_usage_has_token_fields(client: TestClient):
    data = client.get("/v1/usage").json()
    assert "total_tokens" in data or "today" in data or "provider" in data
