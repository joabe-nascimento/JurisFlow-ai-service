"""RAG store com TF-IDF + cosine similarity (scikit-learn)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models import DocumentCreate, KnowledgeDocument, ScoredChunk, SearchResult
from app.rag.chunker import split_chunks

DEFAULT_KNOWLEDGE: List[dict] = [
    {
        "title": "Código de Processo Civil - Prazos",
        "category": "Processual",
        "source": "CPC/2015",
        "content": (
            "Contestação: 15 dias úteis (art. 335 CPC). Apelação: 15 dias. "
            "Embargos de declaração: 5 dias. Agravo de instrumento: 15 dias."
        ),
    },
    {
        "title": "Direito do Trabalho - Reclamação Trabalhista",
        "category": "Trabalhista",
        "source": "CLT + TST",
        "content": (
            "Reclamação trabalhista: prescrição 2 anos durante contrato, 5 após extinção. "
            "Competência: Vara do Trabalho. Honorários: 5% a 15%."
        ),
    },
    {
        "title": "LGPD - Obrigações para Escritórios",
        "category": "Compliance",
        "source": "LGPD Lei 13.709/2018",
        "content": (
            "Política de privacidade, consentimento, segurança, registro de operações "
            "e canal do titular. Dados sensíveis exigem base legal."
        ),
    },
    {
        "title": "Pipeline IA — Python + LangChain",
        "category": "Inteligência Artificial",
        "source": "JurisFlow AI",
        "content": (
            "Stack: Next.js → Spring Boot → FastAPI (Python). RAG com chunking, "
            "TF-IDF/embeddings, retrieval, rerank e geração via LLM. "
            "Evolução: LangChain, Azure OpenAI, vector DB."
        ),
    },
    {
        "title": "Contratos - Cláusulas de Risco",
        "category": "Contratos",
        "source": "Prática advocatícia",
        "content": (
            "Riscos: limitação de responsabilidade, multas desproporcionais, "
            "foro exclusivo, cessão de IP, rescisão sem aviso."
        ),
    },
]


class ChunkRecord:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_title: str,
        category: str,
        content: str,
        source: str = "Manual",
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.category = category
        self.content = content
        self.source = source


class RAGStore:
    def __init__(self) -> None:
        self._documents: Dict[str, Dict[str, KnowledgeDocument]] = {}
        self._chunks: Dict[str, List[ChunkRecord]] = {}
        self._vectorizers: Dict[str, TfidfVectorizer] = {}
        self._matrices: Dict[str, np.ndarray] = {}

    def list_documents(self, escritorio_id: str) -> List[KnowledgeDocument]:
        return list(self._documents.get(escritorio_id, {}).values())

    def add_document(self, escritorio_id: str, data: DocumentCreate) -> KnowledgeDocument:
        self._ensure_escritorio(escritorio_id)
        doc_id = str(uuid.uuid4())
        chunks = split_chunks(data.content)
        doc = KnowledgeDocument(
            id=doc_id,
            title=data.title,
            content=data.content,
            category=data.category or "Geral",
            source=data.source or "Manual",
            chunk_count=len(chunks),
            created_at=datetime.now(timezone.utc),
        )
        self._documents[escritorio_id][doc_id] = doc
        self._index_document_chunks(escritorio_id, doc, chunks)
        self._rebuild_index(escritorio_id)
        return doc

    def remove_document(self, escritorio_id: str, document_id: str) -> bool:
        docs = self._documents.get(escritorio_id)
        if not docs or document_id not in docs:
            return False
        del docs[document_id]
        chunks = self._chunks.get(escritorio_id, [])
        self._chunks[escritorio_id] = [c for c in chunks if c.document_id != document_id]
        self._rebuild_index(escritorio_id)
        return True

    def seed_defaults(self, escritorio_id: str) -> int:
        self._ensure_escritorio(escritorio_id)
        if self._documents[escritorio_id]:
            return 0
        for item in DEFAULT_KNOWLEDGE:
            self.add_document(
                escritorio_id,
                DocumentCreate(
                    title=item["title"],
                    content=item["content"],
                    category=item["category"],
                    source=item["source"],
                ),
            )
        return len(DEFAULT_KNOWLEDGE)

    def search(self, escritorio_id: str, query: str, limit: int = 5) -> SearchResult:
        self._ensure_escritorio(escritorio_id)
        if not self._chunks.get(escritorio_id):
            self.seed_defaults(escritorio_id)

        chunks = self._chunks.get(escritorio_id, [])
        if not chunks or not query.strip():
            return SearchResult(query=query, total_matches=0, chunks=[], retrieval="tfidf")

        matrix = self._matrices.get(escritorio_id)
        vectorizer = self._vectorizers.get(escritorio_id)

        if matrix is None or vectorizer is None or matrix.shape[0] == 0:
            scored = self._lexical_search(chunks, query)
        else:
            scored = self._tfidf_search(chunks, matrix, vectorizer, query)

        scored.sort(key=lambda x: x.score, reverse=True)
        top = [c for c in scored if c.score > 0][:limit]

        return SearchResult(
            query=query,
            total_matches=len([c for c in scored if c.score > 0]),
            chunks=top,
            retrieval="tfidf",
        )

    def build_context(self, search_result: SearchResult) -> str:
        if not search_result.chunks:
            return ""
        parts = [
            f"[Fonte: {c.document_title} | score: {c.score:.3f}]\n{c.content}"
            for c in search_result.chunks
        ]
        return "\n\n---\n\n".join(parts)

    def stats(self) -> Tuple[int, int, int]:
        escritorios = len(self._documents)
        docs = sum(len(d) for d in self._documents.values())
        chunks = sum(len(c) for c in self._chunks.values())
        return escritorios, docs, chunks

    def _ensure_escritorio(self, escritorio_id: str) -> None:
        self._documents.setdefault(escritorio_id, {})
        self._chunks.setdefault(escritorio_id, [])

    def _index_document_chunks(
        self, escritorio_id: str, doc: KnowledgeDocument, chunks: List[str]
    ) -> None:
        for text in chunks:
            self._chunks[escritorio_id].append(
                ChunkRecord(
                    chunk_id=str(uuid.uuid4()),
                    document_id=doc.id,
                    document_title=doc.title,
                    category=doc.category,
                    content=text,
                    source=doc.source,
                )
            )

    def _rebuild_index(self, escritorio_id: str) -> None:
        chunks = self._chunks.get(escritorio_id, [])
        if not chunks:
            self._vectorizers.pop(escritorio_id, None)
            self._matrices.pop(escritorio_id, None)
            return

        texts = [c.content for c in chunks]
        vectorizer = TfidfVectorizer(
            lowercase=True,
            analyzer="word",
            ngram_range=(1, 2),
            max_features=8000,
        )
        matrix = vectorizer.fit_transform(texts)
        self._vectorizers[escritorio_id] = vectorizer
        self._matrices[escritorio_id] = matrix

    def _tfidf_search(
        self,
        chunks: List[ChunkRecord],
        matrix: np.ndarray,
        vectorizer: TfidfVectorizer,
        query: str,
    ) -> List[ScoredChunk]:
        query_vec = vectorizer.transform([query])
        scores = cosine_similarity(query_vec, matrix).flatten()
        result: List[ScoredChunk] = []
        for i, chunk in enumerate(chunks):
            score = float(scores[i])
            if score > 0.01:
                result.append(
                    ScoredChunk(
                        document_id=chunk.document_id,
                        document_title=chunk.document_title,
                        category=chunk.category,
                        content=chunk.content,
                        score=round(score * 100, 2),
                        source=chunk.source,
                    )
                )
        return result

    def _lexical_search(self, chunks: List[ChunkRecord], query: str) -> List[ScoredChunk]:
        terms = {t.lower() for t in query.split() if len(t) > 2}
        result: List[ScoredChunk] = []
        for chunk in chunks:
            lower = chunk.content.lower()
            score = sum(1.0 for t in terms if t in lower)
            if score > 0:
                result.append(
                    ScoredChunk(
                        document_id=chunk.document_id,
                        document_title=chunk.document_title,
                        category=chunk.category,
                        content=chunk.content,
                        score=score,
                        source=chunk.source,
                    )
                )
        return result


rag_store = RAGStore()
