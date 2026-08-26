"""
Testes de validação dos modelos Pydantic — puramente unitários, sem HTTP.

Garante que os contratos de entrada/saída do serviço estão corretos
e que validações obrigatórias funcionam como esperado.
"""
import pytest
from pydantic import ValidationError

from app.models import (
    DocumentCreate,
    JurisprudenceSearchRequest,
    SashaChatRequest,
    SearchRequest,
)


# ---------------------------------------------------------------------------
# SashaChatRequest
# ---------------------------------------------------------------------------

def test_sasha_chat_request_requires_message():
    with pytest.raises(ValidationError):
        SashaChatRequest()  # type: ignore[call-arg]


def test_sasha_chat_request_defaults():
    req = SashaChatRequest(message="Olá", escritorio_id="esc-1")
    assert req.use_rag is True
    assert req.history is None   # Optional, default None
    assert req.mode == "standard"


def test_sasha_chat_request_mode_validation():
    # modo válido
    req = SashaChatRequest(message="msg", escritorio_id="esc", mode="superior")
    assert req.mode == "superior"


def test_sasha_chat_request_history_is_list():
    req = SashaChatRequest(message="msg", escritorio_id="esc")
    assert isinstance(req.history, list)


# ---------------------------------------------------------------------------
# JurisprudenceSearchRequest
# ---------------------------------------------------------------------------

def test_jurisprudence_search_requires_tema():
    with pytest.raises(ValidationError):
        JurisprudenceSearchRequest()  # type: ignore[call-arg]


def test_jurisprudence_search_defaults():
    req = JurisprudenceSearchRequest(tema="horas extras", escritorio_id="esc")
    assert req.tribunal == "Todos"
    assert req.periodo == ""
    assert req.area_juridica == "Geral"


def test_jurisprudence_search_with_tribunal():
    req = JurisprudenceSearchRequest(tema="adicional noturno", tribunal="STJ", escritorio_id="esc")
    assert req.tribunal == "STJ"


# ---------------------------------------------------------------------------
# DocumentCreate
# ---------------------------------------------------------------------------

def test_document_create_requires_title_and_content():
    with pytest.raises(ValidationError):
        DocumentCreate(title="só o título")  # type: ignore[call-arg]


def test_document_create_defaults():
    doc = DocumentCreate(title="Petição", content="Texto da petição")
    assert doc.category == "Geral"
    assert doc.source == "Manual"


# ---------------------------------------------------------------------------
# SearchRequest
# ---------------------------------------------------------------------------

def test_search_request_requires_query():
    with pytest.raises(ValidationError):
        SearchRequest()  # type: ignore[call-arg]


def test_search_request_limit_default():
    req = SearchRequest(query="prazo")
    assert req.limit == 5
