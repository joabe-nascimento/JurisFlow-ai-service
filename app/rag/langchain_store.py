"""RAG Store com LangChain + FAISS (vector store local gratuito)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LangChainDocument

from app.config import settings
from app.models import DocumentCreate, KnowledgeDocument, ScoredChunk, SearchResult

# Dados iniciais (seed)
DEFAULT_KNOWLEDGE: List[dict] = [
    {
        "title": "Código de Processo Civil - Prazos",
        "category": "Processual",
        "source": "CPC/2015",
        "content": (
            "Contestação: 15 dias úteis (art. 335 CPC). Apelação: 15 dias. "
            "Embargos de declaração: 5 dias. Agravo de instrumento: 15 dias. "
            "Recursos especial e extraordinário: 15 dias. "
            "Impugnação ao cumprimento: 15 dias."
        ),
    },
    {
        "title": "Direito do Trabalho - Reclamação Trabalhista",
        "category": "Trabalhista",
        "source": "CLT + TST",
        "content": (
            "Reclamação trabalhista: prescrição 2 anos durante contrato, 5 após extinção. "
            "Competência: Vara do Trabalho. Honorários: 5% a 15%. "
            "Horas extras: 50% dias úteis, 100% domingos/feriados."
        ),
    },
    {
        "title": "LGPD - Obrigações para Escritórios",
        "category": "Compliance",
        "source": "LGPD Lei 13.709/2018",
        "content": (
            "Política de privacidade, consentimento, segurança, registro de operações "
            "e canal do titular. Dados sensíveis exigem base legal específica. "
            "Controlador e operador têm responsabilidades distintas. "
            "ANPD fiscaliza e pode aplicar multas."
        ),
    },
    {
        "title": "RAG com LangChain — Arquitetura",
        "category": "Inteligência Artificial",
        "source": "JurisFlow AI",
        "content": (
            "Stack: Next.js → Spring Boot → FastAPI + LangChain. "
            "RAG: chunking → embeddings (sentence-transformers local) → "
            "FAISS (vector store) → retrieval → rerank → LLM (Groq grátis). "
            "Agents: ReAct pattern com tools (cálculo prazos, busca tribunal). "
            "Chains: análise contrato, pesquisa jurídica, geração de peças."
        ),
    },
    {
        "title": "Contratos - Cláusulas de Risco",
        "category": "Contratos",
        "source": "Prática advocatícia",
        "content": (
            "Riscos: limitação de responsabilidade desigual, multas desproporcionais, "
            "foro exclusivo prejudicial, cessão de IP irrestrita, rescisão sem aviso, "
            "garantias excessivas, renovação automática, sigilo perpétuo."
        ),
    },
    {
        "title": "Honorários Advocatícios — Tabela OAB",
        "category": "Gestão",
        "source": "OAB",
        "content": (
            "Consultoria: 10-20 URH. Contratos: 15-30 URH. "
            "Ação cível: 50-100 URH. Trabalhista: 20-50 URH. "
            "Êxito: 10-30% do valor obtido. URH varia por seccional."
        ),
    },
]


class LangChainRAGStore:
    """
    RAG Store com LangChain + FAISS.
    
    - Embeddings: sentence-transformers/all-MiniLM-L6-v2 (local, gratuito)
    - Vector Store: FAISS (Facebook AI Similarity Search, local)
    - Text Splitter: RecursiveCharacterTextSplitter (chunking inteligente)
    """
    
    def __init__(self):
        self._documents: Dict[str, Dict[str, KnowledgeDocument]] = {}
        self._vector_stores: Dict[str, FAISS] = {}
        self._embeddings = self._init_embeddings()
        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self._persist_dir = Path("data/faiss")
        self._persist_dir.mkdir(parents=True, exist_ok=True)
    
    def _init_embeddings(self) -> HuggingFaceEmbeddings:
        """Inicializa embeddings locais (gratuito, roda em CPU)."""
        return HuggingFaceEmbeddings(
            model_name=settings.embeddings_model,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    
    def list_documents(self, escritorio_id: str) -> List[KnowledgeDocument]:
        """Lista documentos de um escritório."""
        return list(self._documents.get(escritorio_id, {}).values())
    
    def add_document(self, escritorio_id: str, data: DocumentCreate) -> KnowledgeDocument:
        """Adiciona documento e indexa no FAISS."""
        self._ensure_escritorio(escritorio_id)
        
        doc_id = str(uuid.uuid4())
        chunks = self._text_splitter.split_text(data.content)
        
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
        
        # Cria LangChain Documents com metadata
        lc_docs = [
            LangChainDocument(
                page_content=chunk,
                metadata={
                    "document_id": doc_id,
                    "title": doc.title,
                    "category": doc.category,
                    "source": doc.source,
                    "chunk_index": i,
                },
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Adiciona ao vector store
        if escritorio_id not in self._vector_stores:
            self._vector_stores[escritorio_id] = FAISS.from_documents(
                lc_docs, self._embeddings
            )
        else:
            self._vector_stores[escritorio_id].add_documents(lc_docs)
        
        # Persiste FAISS
        self._save_vector_store(escritorio_id)
        
        return doc
    
    def remove_document(self, escritorio_id: str, document_id: str) -> bool:
        """Remove documento (recria vector store sem ele)."""
        docs = self._documents.get(escritorio_id)
        if not docs or document_id not in docs:
            return False
        
        del docs[document_id]
        
        # Recria vector store sem esse documento
        self._rebuild_vector_store(escritorio_id)
        return True
    
    def search(
        self,
        escritorio_id: str,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.3,
    ) -> SearchResult:
        """
        Busca semântica com FAISS.
        
        Args:
            escritorio_id: ID do escritório
            query: Query de busca
            limit: Número máximo de resultados
            score_threshold: Score mínimo (0-1, menor = mais relevante no FAISS)
        """
        self._ensure_escritorio(escritorio_id)
        
        if not self._vector_stores.get(escritorio_id):
            self.seed_defaults(escritorio_id)
        
        vs = self._vector_stores.get(escritorio_id)
        if not vs or not query.strip():
            return SearchResult(
                query=query,
                total_matches=0,
                chunks=[],
                retrieval="langchain-faiss",
            )
        
        # Busca com score (FAISS retorna distância L2, menor = mais similar)
        results = vs.similarity_search_with_score(query, k=limit)
        
        chunks: List[ScoredChunk] = []
        for doc, distance in results:
            # Converte distância L2 para score 0-100 (normaliza)
            similarity = 1 / (1 + distance)  # Transforma distância em similaridade
            score = round(similarity * 100, 2)
            
            if similarity < score_threshold:
                continue
            
            chunks.append(
                ScoredChunk(
                    document_id=doc.metadata.get("document_id", ""),
                    document_title=doc.metadata.get("title", "Sem título"),
                    category=doc.metadata.get("category", "Geral"),
                    content=doc.page_content,
                    score=score,
                )
            )
        
        return SearchResult(
            query=query,
            total_matches=len(chunks),
            chunks=chunks,
            retrieval="langchain-faiss",
        )
    
    def seed_defaults(self, escritorio_id: str) -> int:
        """Popula knowledge base inicial."""
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
    
    def get_vector_store(self, escritorio_id: str) -> Optional[FAISS]:
        """Retorna vector store para uso em chains."""
        return self._vector_stores.get(escritorio_id)
    
    def stats(self) -> tuple[int, int, int]:
        """Retorna (escritorios, documentos, chunks indexados)."""
        escritorios = len(self._documents)
        docs = sum(len(d) for d in self._documents.values())
        chunks = sum(
            vs.index.ntotal for vs in self._vector_stores.values()
            if hasattr(vs.index, "ntotal")
        )
        return escritorios, docs, chunks
    
    def _ensure_escritorio(self, escritorio_id: str) -> None:
        """Garante que escritório existe, carrega FAISS se persistido."""
        if escritorio_id not in self._documents:
            self._documents[escritorio_id] = {}
            self._load_vector_store(escritorio_id)
    
    def _rebuild_vector_store(self, escritorio_id: str) -> None:
        """Reconstroi vector store do zero."""
        docs = list(self._documents.get(escritorio_id, {}).values())
        if not docs:
            self._vector_stores.pop(escritorio_id, None)
            return
        
        lc_docs: List[LangChainDocument] = []
        for doc in docs:
            chunks = self._text_splitter.split_text(doc.content)
            for i, chunk in enumerate(chunks):
                lc_docs.append(
                    LangChainDocument(
                        page_content=chunk,
                        metadata={
                            "document_id": doc.id,
                            "title": doc.title,
                            "category": doc.category,
                            "source": doc.source,
                            "chunk_index": i,
                        },
                    )
                )
        
        if lc_docs:
            self._vector_stores[escritorio_id] = FAISS.from_documents(
                lc_docs, self._embeddings
            )
            self._save_vector_store(escritorio_id)
    
    def _save_vector_store(self, escritorio_id: str) -> None:
        """Persiste FAISS em disco."""
        vs = self._vector_stores.get(escritorio_id)
        if vs:
            path = str(self._persist_dir / escritorio_id)
            vs.save_local(path)
    
    def _load_vector_store(self, escritorio_id: str) -> None:
        """Carrega FAISS do disco se existir."""
        path = self._persist_dir / escritorio_id
        if path.exists():
            try:
                self._vector_stores[escritorio_id] = FAISS.load_local(
                    str(path),
                    self._embeddings,
                    allow_dangerous_deserialization=True,
                )
            except Exception:
                pass  # Se falhar, cria novo


langchain_rag_store = LangChainRAGStore()
