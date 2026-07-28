from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.chains.sasha_assistant import sasha_chat
from app.orchestration.sasha_orchestrator import sasha_orchestrator
from app.chains.contract_analysis import analyze_contract
from app.chains.document_generation import generate_document
from app.chains.document_summary import summarize_document
from app.chains.jurisprudence_analysis import analyze_jurisprudence
from app.chains.jurisprudence_search import search_jurisprudence
from app.chains.case_prediction import predict_case_outcome
from app.chains.legal_research import research
from app.config import settings
from app.llm.errors import LLMRateLimitError
from app.llm.provider import get_provider_info
from app.llm.usage_tracker import get_summary as get_token_usage_summary
from app.middleware.rate_limit import RateLimitMiddleware
from app.verticals.loader import get_current_vertical, list_available_verticals
from app.models import (
    AgentRequest,
    AgentResponse,
    SashaChatRequest,
    SashaChatResponse,
    CaseOutcomeRequest,
    CaseOutcomeResponse,
    ContractAnalysisRequest,
    ContractAnalysisResponse,
    DocumentCreate,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    DocumentSummaryRequest,
    DocumentSummaryResponse,
    JurisprudenceAnalysisRequest,
    JurisprudenceAnalysisResponse,
    JurisprudenceSearchRequest,
    JurisprudenceSearchResponse,
    KnowledgeDocument,
    LegalResearchRequest,
    LegalResearchResponse,
    PipelineRunRequest,
    PipelineRunResult,
    SearchRequest,
    SearchResult,
    StackStatus,
    TokenUsageSummary,
)
from app.pipelines.runner import run_pipeline
from app.rag.factory import get_rag_store

app = FastAPI(
    title=settings.app_name,
    description="🤖 Motor de IA Jurídica — LangChain + RAG + Agents | JurisFlow",
    version="2.0.0",
)

_cors_origins = [
    origin.strip()
    for origin in settings.cors_allowed_origins.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.rate_limit_enabled:
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=settings.rate_limit_per_minute,
    )


# ==================== HEALTH & STATUS ====================

@app.get("/health")
def health():
    return {"status": "ok", "service": "jurisflow-ai-langchain"}


@app.get("/v1/status", response_model=StackStatus)
def stack_status():
    """Status do serviço com info de LLM, RAG e vertical."""
    vertical = get_current_vertical()
    
    store = get_rag_store()
    escritorios, docs, chunks = store.stats()
    
    # Info do LLM
    llm_info = get_provider_info()
    
    capabilities = [
        "FastAPI",
        "LangChain",
        f"RAG ({settings.retrieval_method})",
        "FAISS Vector Store",
        "Embeddings locais",
        f"Vertical: {vertical.name} ({vertical.domain})",
        f"Assistente: {vertical.assistant_name}",
        f"Chains: {len(vertical.chains)}",
        f"Agents: {'enabled' if vertical.agent_enabled else 'disabled'}",
        f"LLM: {llm_info['provider']}",
    ]
    
    return StackStatus(
        service=f"{vertical.name} AI Platform",
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


@app.get("/v1/usage", response_model=TokenUsageSummary)
def token_usage():
    """Consumo acumulado de tokens do LLM (Azure OpenAI, etc.)."""
    summary = get_token_usage_summary()
    llm_info = get_provider_info()
    if not summary.get("provider"):
        summary["provider"] = llm_info.get("provider") or ""
    if not summary.get("model"):
        summary["model"] = llm_info.get("model") or ""
    return TokenUsageSummary(**summary)


@app.get("/v1/verticals")
def get_verticals():
    """Lista verticais disponíveis."""
    available = list_available_verticals()
    current = get_current_vertical()
    
    return {
        "current_vertical": settings.ai_vertical,
        "current_name": current.name,
        "current_domain": current.domain,
        "available_verticals": available,
        "info": "Configure AI_VERTICAL no .env para alterar o vertical ativo"
    }



# ==================== RAG ENDPOINTS ====================

@app.get("/v1/rag/{escritorio_id}/documents", response_model=list[KnowledgeDocument])
def list_documents(escritorio_id: str):
    """Lista documentos indexados."""
    store = get_rag_store()
    store.seed_defaults(escritorio_id)
    return store.list_documents(escritorio_id)


@app.post("/v1/rag/{escritorio_id}/documents", response_model=KnowledgeDocument)
def add_document(escritorio_id: str, body: DocumentCreate):
    """Adiciona documento à base de conhecimento."""
    store = get_rag_store()
    return store.add_document(escritorio_id, body)


@app.delete("/v1/rag/{escritorio_id}/documents/{document_id}")
def remove_document(escritorio_id: str, document_id: str):
    """Remove documento da base."""
    store = get_rag_store()
    if not store.remove_document(escritorio_id, document_id):
        raise HTTPException(status_code=404, detail="Documento não encontrado")
    return {"ok": True}


@app.post("/v1/rag/{escritorio_id}/search", response_model=SearchResult)
def search(escritorio_id: str, body: SearchRequest):
    """Busca semântica/lexical na base de conhecimento."""
    store = get_rag_store()
    return store.search(escritorio_id, body.query, body.limit)


@app.post("/v1/rag/{escritorio_id}/seed")
def seed(escritorio_id: str):
    """Popula base com conhecimento inicial."""
    store = get_rag_store()
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


@app.post("/v1/chains/summarize", response_model=DocumentSummaryResponse)
async def chain_document_summary(body: DocumentSummaryRequest):
    """
    Chain: Resumo de Documentos/Peças Processuais.
    """
    try:
        summary = await summarize_document(body.escritorio_id, body.text)
        return DocumentSummaryResponse(summary=summary, escritorio_id=body.escritorio_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no resumo: {str(e)}")


@app.post("/v1/chains/jurisprudence", response_model=JurisprudenceAnalysisResponse)
async def chain_jurisprudence_analysis(body: JurisprudenceAnalysisRequest):
    """
    Chain: Análise de Jurisprudência com RAG.
    Teses favoráveis/contrárias, súmulas e estratégia.
    """
    try:
        analysis = await analyze_jurisprudence(body.escritorio_id, body.tema, body.area_juridica)
        return JurisprudenceAnalysisResponse(
            analysis=analysis, tema=body.tema, escritorio_id=body.escritorio_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")


@app.post("/v1/chains/jurisprudence-search", response_model=JurisprudenceSearchResponse)
async def chain_jurisprudence_search(body: JurisprudenceSearchRequest):
    """
    Chain: Pesquisa Jurisprudencial Estruturada.
    Retorna julgados/teses relevantes (tribunal, resumo, citação, relevância)
    prontos para alimentar a biblioteca de jurisprudência do escritório.
    """
    try:
        result = await search_jurisprudence(
            body.escritorio_id,
            body.tema,
            body.tribunal,
            body.periodo,
            body.area_juridica,
        )
        return JurisprudenceSearchResponse(
            resultados=result["resultados"],
            disclaimer=result["disclaimer"],
            tema=body.tema,
            escritorio_id=body.escritorio_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na pesquisa: {str(e)}")


@app.post("/v1/chains/predict-outcome", response_model=CaseOutcomeResponse)
async def chain_predict_outcome(body: CaseOutcomeRequest):
    """
    Chain: Análise Preditiva de Resultado de Processo.
    """
    try:
        analysis = await predict_case_outcome(
            body.escritorio_id,
            {
                "area_direito": body.area_direito,
                "tipo_acao": body.tipo_acao,
                "tribunal": body.tribunal,
                "vara": body.vara,
                "resumo": body.resumo,
                "argumentos_autor": body.argumentos_autor,
                "argumentos_reu": body.argumentos_reu,
                "provas": body.provas,
            },
        )
        return CaseOutcomeResponse(analysis=analysis, escritorio_id=body.escritorio_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na previsão: {str(e)}")


# ==================== Sasha ASSISTANT ====================

# Endpoint novo (post-renomeação)
@app.post("/v1/assistant/Sasha/chat", response_model=SashaChatResponse)
async def sasha_chat_endpoint(body: SashaChatRequest):
    """
    Sasha — assistente jurídica conversacional com orchestration inteligente.
    
    Agora usa router que decide automaticamente:
    - Chain (RAG + LLM) para perguntas gerais
    - Agent + tools para buscar processos, prazos, clientes no sistema real
    """
    try:
        history = None
        if body.history:
            history = [{"role": m.role, "content": m.content} for m in body.history]
        
        time_context = None
        if body.time_context:
            time_context = {
                "date": body.time_context.date,
                "time": body.time_context.time,
                "period": body.time_context.period,
            }
        
        # Usa orchestrator em vez da chain simples
        answer, metadata = await sasha_orchestrator(
            escritorio_id=body.escritorio_id,
            message=body.message,
            use_rag=body.use_rag,
            history=history,
            time_context=time_context,
            numero_processo_atual=body.numero_processo_atual,
        )
        
        return SashaChatResponse(
            answer=answer,
            escritorio_id=body.escritorio_id,
            used_rag=body.use_rag,
            usage=get_token_usage_summary().get("today"),
        )
    except LLMRateLimitError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na Sasha: {str(e)}")


# Endpoint legado (compatibilidade com produção antiga)
@app.post("/v1/assistant/bruna/chat", response_model=SashaChatResponse)
async def bruna_chat_endpoint_legacy(body: SashaChatRequest):
    """Alias legado para /Sasha/chat (compatibilidade com deploy antigo)."""
    return await sasha_chat_endpoint(body)


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
        from app.agents.legal_assistant import run_agent

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

