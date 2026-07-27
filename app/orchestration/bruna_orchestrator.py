"""Orchestrator da Bruna - decide entre chain simples ou agent com tools."""

from __future__ import annotations

from typing import Optional

from app.chains.bruna_assistant import bruna_chat
from app.config import settings
from app.llm.errors import LLMRateLimitError
from app.orchestration.router import route_query
from app.tools.integration_api import integration_tools
from app.agents.tools import legal_tools


async def bruna_orchestrator(
    escritorio_id: str,
    message: str,
    use_rag: bool = True,
    history: Optional[list] = None,
    time_context: Optional[dict] = None,
) -> tuple[str, dict]:
    """
    Orchestrator da Bruna que decide a melhor estratégia.

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

        all_tools = legal_tools + integration_tools

        result = await run_legal_agent(
            question=message,
            escritorio_id=escritorio_id,
            mode="full",
        )

        steps = result.get("steps", [])
        metadata["tools_used"] = [step.get("tool") for step in steps] if steps else []
        metadata["iterations"] = result.get("iterations", 0)
        answer = result.get("answer", "Não consegui processar sua solicitação.")
    else:
        answer = await bruna_chat(
            escritorio_id=escritorio_id,
            message=message,
            use_rag=use_rag,
            history=history,
            time_context=time_context,
        )
        metadata["tools_used"] = []

    return answer, metadata
