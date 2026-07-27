"""Factory para RAG store com carregamento lazy."""

from app.config import settings

_rag_store = None
_langchain_rag_store = None


def get_rag_store():
    """Retorna o store configurado sem carregar embeddings pesados quando usa TF-IDF."""
    global _rag_store, _langchain_rag_store

    if settings.retrieval_method == "langchain":
        if _langchain_rag_store is None:
            from app.rag.langchain_store import langchain_rag_store as lc_store

            _langchain_rag_store = lc_store
        return _langchain_rag_store

    if _rag_store is None:
        from app.rag.store import rag_store

        _rag_store = rag_store
    return _rag_store
