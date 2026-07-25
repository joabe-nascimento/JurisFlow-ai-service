"""Orchestrator da Bruna - decide entre chain simples ou agent com tools."""

from typing import Optional

from app.chains.bruna_assistant import bruna_chat
from app.orchestration.router import route_query
from app.agents.legal_assistant import run_agent as run_legal_agent
from app.tools.java_api import java_api_tools
from app.agents.tools import legal_tools


async def bruna_orchestrator(
    escritorio_id: str,
    message: str,
    use_rag: bool = True,
    history: Optional[list] = None,
) -> tuple[str, dict]:
    """
    Orchestrator da Bruna que decide a melhor estratégia.
    
    Fluxo:
    1. Classifica intenção da pergunta
    2. Decide: agent (com tools) ou chain (RAG + LLM direto)
    3. Executa estratégia escolhida
    4. Retorna resposta + metadados
    
    Returns:
        (resposta, metadata)
        metadata: {"strategy": "agent"|"chain", "intent": str, "tools_used": [...]}
    """
    
    # Classifica e roteia
    decision, strategy = await route_query(message, escritorio_id, history)
    
    metadata = {
        "strategy": strategy,
        "intent": decision.intent.value,
        "explanation": decision.explanation,
        "use_agent": decision.use_agent,
        "use_rag": decision.use_rag,
    }
    
    try:
        if strategy == "agent":
            # Usa agent com tools (Java API + cálculos)
            # Combina tools jurídicas + tools da API Java
            all_tools = legal_tools + java_api_tools
            
            result = await run_legal_agent(
                question=message,
                escritorio_id=escritorio_id,
                mode="full",
            )
            
            # Extrai tools usadas dos steps
            steps = result.get("steps", [])
            metadata["tools_used"] = [step.get("tool") for step in steps] if steps else []
            metadata["iterations"] = result.get("iterations", 0)
            
            answer = result.get("answer", "Não consegui processar sua solicitação.")
            
        else:
            # Usa chain simples (Bruna conversacional)
            answer = await bruna_chat(
                escritorio_id=escritorio_id,
                message=message,
                use_rag=use_rag,
                history=history,
            )
            
            metadata["tools_used"] = []
        
        return answer, metadata
        
    except Exception as e:
        # Fallback para chain em caso de erro
        metadata["error"] = str(e)
        metadata["fallback"] = True
        
        answer = await bruna_chat(
            escritorio_id=escritorio_id,
            message=message,
            use_rag=use_rag,
            history=history,
        )
        
        return answer, metadata
