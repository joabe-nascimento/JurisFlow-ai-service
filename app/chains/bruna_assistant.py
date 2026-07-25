"""Assistente conversacional com RAG + LLM (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.errors import LLMRateLimitError, is_rate_limit_error
from app.llm.provider import (
    get_llm_by_provider,
    get_openrouter_model_list,
    get_provider_attempt_order,
)
from app.rag.langchain_store import langchain_rag_store
from app.verticals.loader import get_current_vertical


def _format_history(history: list | None) -> str:
    if not history:
        return "Sem histórico anterior."
    lines = []
    for msg in history[-6:]:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            label = "Advogado" if role == "user" else "Bruna"
            content = (msg.get("content") or "")[:800]
            lines.append(f"{label}: {content}")
    return "\n".join(lines)


def _retrieve_context(escritorio_id: str, message: str, use_rag: bool) -> str:
    if not use_rag:
        return "RAG desabilitado para esta conversa."
    result = langchain_rag_store.search(escritorio_id, message, limit=4)
    if not result.chunks:
        langchain_rag_store.seed_defaults(escritorio_id)
        result = langchain_rag_store.search(escritorio_id, message, limit=4)
    if not result.chunks:
        return "Nenhum documento relevante na base do escritório."
    return "\n\n---\n\n".join(
        f"**{c.document_title}** ({c.category})\n{c.content}"
        for c in result.chunks
    )


def _build_chain(llm):
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt(vertical.assistant_prompt_file)
    
    template = prompt_config["system_prompt"].format(
        assistant_name=vertical.assistant_name,
        product_name=vertical.name,
        context="{context}",
        history="{history}",
        message="{message}",
    )
    
    prompt = ChatPromptTemplate.from_template(template)

    def prepare(inputs: dict) -> dict:
        return {
            "message": inputs["message"],
            "context": _retrieve_context(
                inputs["escritorio_id"], inputs["message"], inputs["use_rag"]
            ),
            "history": _format_history(inputs.get("history")),
        }

    return prepare | prompt | llm | StrOutputParser()


async def bruna_chat(
    escritorio_id: str,
    message: str,
    use_rag: bool = True,
    history: list | None = None,
) -> str:
    """Chat conversacional com Bruna (1 chamada LLM + RAG), com fallback de provider."""
    inputs = {
        "message": message,
        "escritorio_id": escritorio_id,
        "use_rag": use_rag,
        "history": history,
    }

    providers = get_provider_attempt_order()
    last_rate_limit: Exception | None = None

    for provider in providers:
        models = (
            get_openrouter_model_list()
            if provider == "openrouter"
            else [None]
        )
        for model_id in models:
            try:
                llm = get_llm_by_provider(
                    provider,
                    temperature=0.4,
                    max_tokens=1024,
                    model=model_id,
                )
                chain = _build_chain(llm)
                return await chain.ainvoke(inputs)
            except Exception as exc:
                if is_rate_limit_error(exc):
                    last_rate_limit = exc
                    # Limite diário da conta — outros modelos :free não ajudam
                    if "free-models-per-day" in str(exc).lower():
                        break
                    continue
                raise
        if last_rate_limit and "free-models-per-day" in str(last_rate_limit).lower():
            break

    raise LLMRateLimitError(
        "Limite diário do provedor LLM atingido (OpenRouter free: 50 req/dia). "
        "Configure AZURE_OPENAI_KEY/AZURE_OPENAI_ENDPOINT no .env como fallback "
        "ou aguarde o reset do provedor. "
        f"Detalhe: {last_rate_limit}"
    )
