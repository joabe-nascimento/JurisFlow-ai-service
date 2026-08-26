"""
Testes do RAG store via endpoints REST — usa TF-IDF (scikit-learn), sem FAISS.

Todos os endpoints são ASGI (TestClient), sem servidor real.
Os dados persistem em memória durante a sessão de testes.
"""
import pytest
from fastapi.testclient import TestClient


ESC = "esc-rag-pytest"


def test_seed_populates_base(client: TestClient):
    r = client.post(f"/v1/rag/{ESC}/seed")
    assert r.status_code == 200
    data = r.json()
    assert "seeded" in data
    assert data["total"] >= data["seeded"]


def test_list_documents_returns_list(client: TestClient):
    client.post(f"/v1/rag/{ESC}/seed")
    r = client.get(f"/v1/rag/{ESC}/documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_documents_not_empty_after_seed(client: TestClient):
    client.post(f"/v1/rag/{ESC}/seed")
    docs = client.get(f"/v1/rag/{ESC}/documents").json()
    assert len(docs) > 0


def test_add_document_returns_knowledge_document(client: TestClient):
    payload = {
        "title": "Prazo para Embargos de Declaração",
        "content": "O prazo para oposição de embargos de declaração é de 5 dias úteis.",
        "category": "Processual",
        "source": "CPC art. 1.023",
    }
    r = client.post(f"/v1/rag/{ESC}/documents", json=payload)
    assert r.status_code == 200
    doc = r.json()
    assert doc["title"] == payload["title"]
    assert "id" in doc


def test_add_document_appears_in_list(client: TestClient):
    payload = {
        "title": "Habeas Corpus — requisitos",
        "content": "HC cabível quando há ilegalidade ou abuso de poder que ameace a liberdade.",
        "category": "Constitucional",
        "source": "CF art. 5º LXVIII",
    }
    client.post(f"/v1/rag/{ESC}/documents", json=payload)
    docs = client.get(f"/v1/rag/{ESC}/documents").json()
    titles = [d["title"] for d in docs]
    assert payload["title"] in titles


def test_search_returns_chunks(client: TestClient):
    client.post(f"/v1/rag/{ESC}/seed")
    r = client.post(f"/v1/rag/{ESC}/search", json={"query": "prazo contestação", "limit": 3})
    assert r.status_code == 200
    data = r.json()
    assert "chunks" in data
    assert isinstance(data["chunks"], list)


def test_search_respects_limit(client: TestClient):
    client.post(f"/v1/rag/{ESC}/seed")
    limit = 2
    r = client.post(f"/v1/rag/{ESC}/search", json={"query": "LGPD obrigações", "limit": limit})
    chunks = r.json()["chunks"]
    assert len(chunks) <= limit


def test_search_has_score_field(client: TestClient):
    client.post(f"/v1/rag/{ESC}/seed")
    r = client.post(f"/v1/rag/{ESC}/search", json={"query": "honorários advocatícios", "limit": 3})
    for chunk in r.json()["chunks"]:
        assert "score" in chunk
        assert isinstance(chunk["score"], (int, float))


def test_delete_document_removes_from_list(client: TestClient):
    payload = {
        "title": "Doc para deletar",
        "content": "Conteúdo temporário de teste que será removido.",
        "category": "Teste",
        "source": "pytest",
    }
    esc = "esc-delete-pytest"
    add_r = client.post(f"/v1/rag/{esc}/documents", json=payload)
    doc_id = add_r.json()["id"]

    del_r = client.delete(f"/v1/rag/{esc}/documents/{doc_id}")
    assert del_r.status_code == 200
    assert del_r.json()["ok"] is True

    docs = client.get(f"/v1/rag/{esc}/documents").json()
    assert not any(d["id"] == doc_id for d in docs)


def test_delete_nonexistent_document_returns_404(client: TestClient):
    r = client.delete(f"/v1/rag/{ESC}/documents/id-que-nao-existe")
    assert r.status_code == 404
