from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agents.legal_assistant import run_agent
from app.chains.bruna_assistant import bruna_chat
from app.orchestration.bruna_orchestrator import bruna_orchestrator
from app.chains.contract_analysis import analyze_contract
from app.chains.document_generation import generate_document
from app.chains.legal_research import research
from app.config import settings
from app.llm.errors import LLMRateLimitError
from app.llm.provider import get_provider_info
from app.models import (
    AgentRequest,
    AgentResponse,
    BrunaChatRequest,
    BrunaChatResponse,
    ContractAnalysisRequest,
    ContractAnalysisResponse,
    DocumentCreate,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    KnowledgeDocument,
    LegalResearchRequest,
    LegalResearchResponse,
    PipelineRunRequest,
    PipelineRunResult,
    SearchRequest,
    SearchResult,
    StackStatus,
)
from app.pipelines.runner import run_pipeline
from app.rag.langchain_store import langchain_rag_store
from app.rag.store import rag_store

app = FastAPI(
    title=settings.app_name,
    description="🤖 Motor de IA Jurídica — LangChain + RAG + Agents | JurisFlow",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== HEALTH & STATUS ====================

@app.get("/health")
def health():
    return {"status": "ok", "service": "jurisflow-ai-langchain"}


@app.get("/v1/status", response_model=StackStatus)
def stack_status():
    """Status do serviço com info de LLM e RAG."""
    
    # Usa o store configurado
    if settings.retrieval_method == "langchain":
        escritorios, docs, chunks = langchain_rag_store.stats()
    else:
        escritorios, docs, chunks = rag_store.stats()
    
    # Info do LLM
    llm_info = get_provider_info()
    
    capabilities = [
        "FastAPI",
        "LangChain",
        f"RAG ({settings.retrieval_method})",
        "FAISS Vector Store",
        "Embeddings locais",
        "Chains (análise, pesquisa, geração)",
        "Agents com Tools",
        f"LLM: {llm_info['provider']}",
    ]
    
    return StackStatus(
        service="JurisFlow AI + LangChain",
        version="2.0.0",
        status="online",
        retrieval=settings.retrieval_method,
        capabilities=capabilities,
        escritorios_indexed=escritorios,
        total_documents=docs,
        total_chunks=chunks,
        llm_provider=llm_info["provider"],
        llm_model=llm_info["model"],
        llm_cost=llm_info["cost"],
    )



# ==================== RAG ENDPOINTS ====================

@app.get("/v1/rag/{escritorio_id}/documents", response_model=list[KnowledgeDocument])
def list_documents(escritorio_id: str):
    """Lista documentos indexados."""
    store = langchain_rag_store if settings.retrieval_method == "langchain" else rag_store
    store.seed_defaults(escritorio_id)
    return store.list_documents(escritorio_id)


@app.post("/v1/rag/{escritorio_id}/documents", response_model=KnowledgeDocument)
def add_document(escritorio_id: str, body: DocumentCreate):
    """Adiciona documento à base de conhecimento."""
    store = langchain_rag_store if settings.retrieval_method == "langchain" else rag_store
    return store.add_document(escritorio_id, body)


@app.delete("/v1/rag/{escritorio_id}/documents/{document_id}")
def remove_document(escritorio_id: str, document_id: str):
    """Remove documento da base."""
    store = langchain_rag_store if settings.retrieval_method == "langchain" else rag_store
    if not store.remove_document(escritorio_id, document_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return {"ok": True}


@app.post("/v1/rag/{escritorio_id}/search", response_model=SearchResult)
def search(escritorio_id: str, body: SearchRequest):
    """Busca semântica/lexical na base de conhecimento."""
    store = langchain_rag_store if settings.retrieval_method == "langchain" else rag_store
    return store.search(escritorio_id, body.query, body.limit)


@app.post("/v1/rag/{escritorio_id}/seed")
def seed(escritorio_id: str):
    """Popula base com conhecimento inicial."""
    store = langchain_rag_store if settings.retrieval_method == "langchain" else rag_store
    count = store.seed_defaults(escritorio_id)
    return {"seeded": count, "total": len(store.list_documents(escritorio_id))}


# ==================== LANGCHAIN CHAINS ====================

@app.post("/v1/chains/contract-analysis", response_model=ContractAnalysisResponse)
async def chain_contract_analysis(body: ContractAnalysisRequest):
    """
    Chain: Análise de Contratos com RAG.
    Identifica cláusulas de risco e sugere ajustes.
    """
    try:
        analysis = await analyze_contract(body.escritorio_id, body.contract_text)
        return ContractAnalysisResponse(
            analysis=analysis,
            escritorio_id=body.escritorio_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.post("/v1/chains/legal-research", response_model=LegalResearchResponse)
async def chain_legal_research(body: LegalResearchRequest):
    """
    Chain: Pesquisa Jurídica com RAG.
    Responde perguntas baseadas na base de conhecimento.
    """
    try:
        answer = await research(body.escritorio_id, body.question)
        return LegalResearchResponse(
            answer=answer,
            question=body.question,
            escritorio_id=body.escritorio_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na pesquisa: {str(e)}")


@app.post("/v1/chains/document-generation", response_model=DocumentGenerationResponse)
async def chain_document_generation(body: DocumentGenerationRequest):
    """
    Chain: Geração de Documentos Jurídicos.
    Gera minutas de petições, contratos, procurações, etc.
    """
    try:
        document = await generate_document(
            body.escritorio_id,
            body.document_type,
            body.data,
        )
        return DocumentGenerationResponse(
            document=document,
            document_type=body.document_type,
            escritorio_id=body.escritorio_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")


# ==================== BRUNA ASSISTANT ====================

@app.post("/v1/assistant/bruna/chat", response_model=BrunaChatResponse)
async def bruna_chat_endpoint(body: BrunaChatRequest):
    """
    Bruna — assistente jurídica conversacional com orchestration inteligente.
    
    Agora usa router que decide automaticamente:
    - Chain (RAG + LLM) para perguntas gerais
    - Agent + tools para buscar processos, prazos, clientes no sistema real
    """
    try:
        history = None
        if body.history:
            history = [{"role": m.role, "content": m.content} for m in body.history]
        
        # Usa orchestrator em vez da chain simples
        answer, metadata = await bruna_orchestrator(
            escritorio_id=body.escritorio_id,
            message=body.message,
            use_rag=body.use_rag,
            history=history,
        )
        
        return BrunaChatResponse(
            answer=answer,
            escritorio_id=body.escritorio_id,
            used_rag=body.use_rag,
        )
    except LLMRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na Bruna: {str(e)}")


# ==================== LANGCHAIN AGENTS ====================

@app.post("/v1/agent/ask", response_model=AgentResponse)
async def agent_ask(body: AgentRequest):
    """
    Agente Jurídico com Tools (ReAct pattern).
    
    O agente tem acesso a:
    - calcular_prazo: Calcula prazos processuais
    - buscar_conhecimento: Busca no RAG
    - buscar_jurisprudencia: Busca jurisprudência (simulado)
    - calcular_honorarios: Calcula honorários OAB
    
    Exemplos de perguntas:
    - "Qual o prazo para apelar? Hoje é 01/01/2024"
    - "Busque informações sobre LGPD"
    - "Calcule honorários para ação cível de R$ 50.000"
    """
    if not settings.agent_enabled:
        raise HTTPException(status_code=503, detail="Agent desabilitado na configuração")
    
    try:
        result = await run_agent(
            body.question,
            body.escritorio_id,
            body.mode,  # type: ignore
        )
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no agente: {str(e)}")


# ==================== PIPELINES (legado) ====================

@app.post("/v1/pipelines/run", response_model=PipelineRunResult)
def pipeline_run(body: PipelineRunRequest):
    """Pipeline cognitivo (legado - considere usar chains/agent)."""
    return run_pipeline(body)
