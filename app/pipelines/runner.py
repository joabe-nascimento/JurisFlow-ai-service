import time
from typing import List

from app.config import settings
from app.models import PipelineRunRequest, PipelineRunResult, PipelineStepResult
from app.rag.factory import get_rag_store

PIPELINES = {
    "rag-chat": {
        "name": "RAG + Chat (Python)",
        "steps": ["retrieve", "augment", "generate"],
    },
    "agent-orchestration": {
        "name": "Orquestração de Agentes",
        "steps": ["route", "retrieve", "agent", "validate"],
    },
    "document-analysis": {
        "name": "Análise de Documento",
        "steps": ["chunk", "summarize", "extract", "risk"],
    },
    "azure-copilot": {
        "name": "Azure Copilot Studio",
        "steps": ["auth", "foundry", "openai", "copilot"],
    },
}


def run_pipeline(request: PipelineRunRequest) -> PipelineRunResult:
    meta = PIPELINES.get(request.pipeline_id)
    if not meta:
        return PipelineRunResult(
            success=False,
            pipeline_id=request.pipeline_id,
            pipeline_name="Desconhecido",
            content="Pipeline não encontrado.",
            steps=[],
            total_duration_ms=0,
        )

    steps: List[PipelineStepResult] = []
    total_ms = 0
    rag_context = ""

    if request.use_rag:
        start = time.perf_counter()
        
        # Usa o store configurado (LangChain FAISS ou TF-IDF)
        store = get_rag_store()
        search = store.search(request.escritorio_id, request.input, 4)
        
        # Build context
        if hasattr(store, 'build_context'):
            rag_context = store.build_context(search)
        else:
            # LangChain store não tem build_context, cria manual
            rag_context = "\n\n".join([
                f"[{c.document_title}] {c.content}" for c in search.chunks
            ])
        
        ms = int((time.perf_counter() - start) * 1000)
        total_ms += ms
        
        retrieval_method = "LangChain FAISS" if settings.retrieval_method == "langchain" else "TF-IDF"
        steps.append(
            PipelineStepResult(
                step_id="retrieve",
                name=f"Retrieval ({retrieval_method})",
                status="completed",
                output=f"{len(search.chunks)} chunks · {search.retrieval}",
                duration_ms=ms,
            )
        )

    for step_id in meta["steps"]:
        if step_id == "retrieve" and request.use_rag:
            continue
        ms = 60 + len(steps) * 35
        total_ms += ms
        steps.append(
            PipelineStepResult(
                step_id=step_id,
                name=step_id.replace("-", " ").title(),
                status="completed",
                output="OK — processado pelo motor Python",
                duration_ms=ms,
            )
        )

    content = _demo_response(request.input, rag_context, meta["name"])

    return PipelineRunResult(
        success=True,
        pipeline_id=request.pipeline_id,
        pipeline_name=meta["name"],
        content=content,
        steps=steps,
        total_duration_ms=total_ms + 120,
        engine="python",
    )


def _demo_response(input_text: str, rag_context: str, pipeline_name: str) -> str:
    lower = input_text.lower()
    header = f"**{pipeline_name}** · Motor Python (FastAPI + scikit-learn)\n\n"

    if rag_context:
        header += "_Contexto RAG recuperado via TF-IDF cosine similarity._\n\n"

    if "prazo" in lower or "contestação" in lower:
        body = (
            "Prazos CPC indexados: contestação 15 dias úteis, apelação 15 dias, "
            "embargos 5 dias. Confirme intimação no DJE."
        )
    elif "contrato" in lower:
        body = "Análise de cláusulas: revisar SLA, LGPD, rescisão e limitação de responsabilidade."
    elif "trabalh" in lower:
        body = "Teses trabalhistas: verbas rescisórias, jornada, honorários sucumbenciais (TST)."
    else:
        body = (
            "Pipeline executado com retrieval Python. "
            "Configure OPENAI_API_KEY para geração LLM completa."
        )

    if rag_context:
        preview = rag_context[:280].replace("\n", " ")
        body += f"\n\n**Preview RAG:** {preview}..."

    return header + body
