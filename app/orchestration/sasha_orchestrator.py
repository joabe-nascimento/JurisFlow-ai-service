"""Orchestrator da Sasha - decide entre chain simples ou agent com tools."""

from __future__ import annotations

from typing import Optional

from app.chains.sasha_assistant import sasha_chat
from app.config import settings
from app.llm.errors import LLMRateLimitError
from app.orchestration.router import route_query
from app.tools.integration_api import get_integration_tools
from app.agents.tools import legal_tools


async def sasha_orchestrator(
    escritorio_id: str,
    message: str,
    use_rag: bool = True,
    history: Optional[list] = None,
    time_context: Optional[dict] = None,
    numero_processo_atual: Optional[str] = None,
) -> tuple[str, dict]:
    """
    Orchestrator da Sasha que decide a melhor estratégia.

    Returns:
        (resposta, metadata)
    """
    decision, strategy = await route_query(message, escritorio_id, history)

    metadata = {
        "strategy": strategy,
        "intent": decision.intent.value,
        "explanation": decision.explanation,
        "use_agent": decision.use_agent,
        "use_rag": decision.use_rag,
    }

    if strategy == "agent" and settings.agent_enabled:
        from app.agents.legal_assistant import run_agent as run_legal_agent

        # escritorio_id vem do backend (payload autenticado), nunca do LLM —
        # as tools de integração já saem com o tenant fixado via closure.
        all_tools = legal_tools + get_integration_tools(escritorio_id)

        question = message
        if numero_processo_atual:
            question = (
                f"(Contexto: o usuário está vendo o processo {numero_processo_atual} na tela agora; "
                f"se a pergunta não citar outro número, considere que é sobre este processo)\n{message}"
            )

        result = await run_legal_agent(
            question=question,
            escritorio_id=escritorio_id,
            mode="full",
            tools=all_tools,
        )

        steps = result.get("steps", [])
        metadata["tools_used"] = [step.get("tool") for step in steps] if steps else []
        metadata["iterations"] = result.get("iterations", 0)
        answer = result.get("answer", "Não consegui processar sua solicitação.")
    else:
        answer = await sasha_chat(
            escritorio_id=escritorio_id,
            message=message,
            use_rag=use_rag,
            history=history,
            time_context=time_context,
            numero_processo_atual=numero_processo_atual,
        )
        metadata["tools_used"] = []

    return answer, metadata

