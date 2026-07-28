from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    id: str
    title: str
    content: str
    category: str = "Geral"
    source: str = "Manual"
    chunk_count: int = 0
    created_at: Optional[datetime] = None


class DocumentCreate(BaseModel):
    title: str
    content: str
    category: Optional[str] = "Geral"
    source: Optional[str] = "Manual"


class ScoredChunk(BaseModel):
    document_id: str
    document_title: str
    category: str
    content: str
    score: float


class SearchRequest(BaseModel):
    query: str
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    query: str
    total_matches: int
    chunks: List[ScoredChunk]
    retrieval: str = "tfidf"


class PipelineStepResult(BaseModel):
    step_id: str
    name: str
    status: str
    output: str
    duration_ms: int


class PipelineRunRequest(BaseModel):
    pipeline_id: str
    input: str
    use_rag: bool = True
    escritorio_id: str


class PipelineRunResult(BaseModel):
    success: bool
    pipeline_id: str
    pipeline_name: str
    content: str
    steps: List[PipelineStepResult]
    total_duration_ms: int
    engine: str = "python"


class StackStatus(BaseModel):
    service: str
    version: str
    status: str
    retrieval: str
    capabilities: List[str]
    escritorios_indexed: int
    total_documents: int
    total_chunks: int
    llm_provider: Optional[str] = None
    llm_model: Optional[str] = None
    llm_cost: Optional[str] = None


# ==================== LANGCHAIN MODELS ====================

class ContractAnalysisRequest(BaseModel):
    contract_text: str = Field(..., description="Texto do contrato a ser analisado")
    escritorio_id: str = Field(default="default")


class ContractAnalysisResponse(BaseModel):
    analysis: str
    escritorio_id: str


class LegalResearchRequest(BaseModel):
    question: str = Field(..., description="Pergunta jurídica")
    escritorio_id: str = Field(default="default")


class LegalResearchResponse(BaseModel):
    answer: str
    question: str
    escritorio_id: str


class DocumentGenerationRequest(BaseModel):
    document_type: str = Field(..., description="Tipo: petição, contrato, procuração, etc")
    data: str = Field(..., description="Dados para preenchimento (JSON ou texto)")
    escritorio_id: str = Field(default="default")


class DocumentGenerationResponse(BaseModel):
    document: str
    document_type: str
    escritorio_id: str


class DocumentSummaryRequest(BaseModel):
    text: str = Field(..., description="Texto do documento a ser resumido")
    escritorio_id: str = Field(default="default")


class DocumentSummaryResponse(BaseModel):
    summary: str
    escritorio_id: str


class JurisprudenceAnalysisRequest(BaseModel):
    tema: str = Field(..., description="Tema jurídico a analisar")
    area_juridica: str = Field(default="Geral", description="Área do direito")
    escritorio_id: str = Field(default="default")


class JurisprudenceAnalysisResponse(BaseModel):
    analysis: str
    tema: str
    escritorio_id: str


class JurisprudenceSearchRequest(BaseModel):
    tema: str = Field(..., description="Tema, palavra-chave ou pergunta jurídica")
    tribunal: str = Field(default="Todos", description="Tribunal alvo: STF, STJ, TST, TRT, TJ, Todos...")
    periodo: str = Field(default="", description="Recorte temporal, ex.: 'últimos 3 anos'")
    area_juridica: str = Field(default="Geral", description="Área do direito")
    escritorio_id: str = Field(default="default")


class JurisprudenceSearchItem(BaseModel):
    tribunal: str
    tema: str
    resultado: Optional[str] = None
    relevancia: str = "media"
    referencia: Optional[str] = None
    resumo: Optional[str] = None


class JurisprudenceSearchResponse(BaseModel):
    resultados: list[JurisprudenceSearchItem]
    disclaimer: str
    tema: str
    escritorio_id: str


class CaseOutcomeRequest(BaseModel):
    area_direito: str = Field(default="")
    tipo_acao: str = Field(default="")
    tribunal: str = Field(default="")
    vara: str = Field(default="")
    resumo: str = Field(default="")
    argumentos_autor: str = Field(default="")
    argumentos_reu: str = Field(default="")
    provas: str = Field(default="")
    escritorio_id: str = Field(default="default")


class CaseOutcomeResponse(BaseModel):
    analysis: str
    escritorio_id: str


class AgentRequest(BaseModel):
    question: str = Field(..., description="Pergunta para o agente")
    escritorio_id: str = Field(default="default")
    mode: str = Field(default="full", description="full | answer_only")


class AgentStep(BaseModel):
    tool: str
    input: dict
    output: str


class AgentResponse(BaseModel):
    answer: str
    steps: Optional[List[AgentStep]] = None
    iterations: Optional[int] = None
    error: Optional[bool] = None


# ==================== Sasha ASSISTANT ====================

class ChatHistoryMessage(BaseModel):
    role: str
    content: str


class TimeContext(BaseModel):
    """Contexto temporal para dar consciência de data/hora à IA."""
    date: str = Field(..., description="Data formatada (ex: sexta-feira, 25 de julho de 2026)")
    time: str = Field(..., description="Hora formatada (ex: 23:30)")
    period: str = Field(..., description="Período do dia: manhã, tarde ou noite")


class SashaChatRequest(BaseModel):
    message: str = Field(..., description="Mensagem do usuário")
    escritorio_id: str = Field(default="default")
    use_rag: bool = Field(default=True)
    history: Optional[List[ChatHistoryMessage]] = None
    time_context: Optional[TimeContext] = None


class SashaChatResponse(BaseModel):
    answer: str
    assistant: str = "Sasha"
    escritorio_id: str
    used_rag: bool = True
    usage: Optional[dict] = None


class TokenUsageSummary(BaseModel):
    provider: str = ""
    model: str = ""
    lifetime: dict = Field(default_factory=dict)
    today: dict = Field(default_factory=dict)
    month: dict = Field(default_factory=dict)
    last_request_at: Optional[str] = None

