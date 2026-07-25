"""Router inteligente que decide a melhor estratégia para cada pergunta."""

from typing import Literal, Optional
from enum import Enum

from app.llm.provider import get_llm


class QueryIntent(str, Enum):
    """Tipos de intenção identificados."""
    BUSCAR_PROCESSO = "buscar_processo"
    VERIFICAR_PRAZO = "verificar_prazo"
    BUSCAR_CLIENTE = "buscar_cliente"
    CALCULAR_PRAZO = "calcular_prazo"
    PESQUISA_JURIDICA = "pesquisa_juridica"
    CONVERSACIONAL = "conversacional"


class RouteDecision:
    """Decisão do router sobre como processar a query."""
    
    def __init__(
        self,
        intent: QueryIntent,
        use_agent: bool,
        use_rag: bool,
        explanation: str,
        extracted_entities: Optional[dict] = None
    ):
        self.intent = intent
        self.use_agent = use_agent
        self.use_rag = use_rag
        self.explanation = explanation
        self.extracted_entities = extracted_entities or {}


async def classify_query_intent(message: str) -> RouteDecision:
    """
    Classifica a intenção da pergunta e decide a estratégia.
    
    Lógica de decisão:
    - Buscar processo/cliente/prazo específico → use_agent=True (precisa de tools)
    - Cálculo de prazo → use_agent=True (tool calcular_prazo)
    - Pesquisa jurídica geral → use_agent=False, use_rag=True
    - Conversação geral → use_agent=False, use_rag=True
    """
    
    message_lower = message.lower()
    
    # Padrões de detecção simples (pode ser melhorado com LLM)
    
    # Busca de processo (número específico)
    if any(pattern in message_lower for pattern in ["processo", "nº", "numero"]):
        # Tenta extrair número de processo
        import re
        processo_pattern = r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}'
        match = re.search(processo_pattern, message)
        if match:
            return RouteDecision(
                intent=QueryIntent.BUSCAR_PROCESSO,
                use_agent=True,
                use_rag=False,
                explanation="Detectado número de processo - usando agent com tool buscar_processo",
                extracted_entities={"numero_processo": match.group()}
            )
    
    # Verificação de prazos
    if any(pattern in message_lower for pattern in ["prazo", "vencimento", "vence", "quando vence"]):
        # Se menciona processo específico, usa agent
        if "processo" in message_lower or any(c.isdigit() for c in message):
            return RouteDecision(
                intent=QueryIntent.VERIFICAR_PRAZO,
                use_agent=True,
                use_rag=True,
                explanation="Pergunta sobre prazo com possível referência a processo - usando agent"
            )
        # Se pergunta sobre prazo genérico (ex: "qual o prazo para contestar")
        else:
            return RouteDecision(
                intent=QueryIntent.PESQUISA_JURIDICA,
                use_agent=False,
                use_rag=True,
                explanation="Pergunta sobre prazo genérico - usando RAG + LLM direto"
            )
    
    # Busca de cliente
    if any(pattern in message_lower for pattern in ["cliente", "contato", "telefone do cliente"]):
        return RouteDecision(
            intent=QueryIntent.BUSCAR_CLIENTE,
            use_agent=True,
            use_rag=False,
            explanation="Busca de cliente - usando agent com tool buscar_cliente"
        )
    
    # Cálculo de prazo (com data específica)
    if any(pattern in message_lower for pattern in ["calcular prazo", "contar", "a partir de"]):
        if any(c.isdigit() for c in message):  # Tem data
            return RouteDecision(
                intent=QueryIntent.CALCULAR_PRAZO,
                use_agent=True,
                use_rag=True,
                explanation="Cálculo de prazo com data - usando agent com tool calcular_prazo"
            )
    
    # Pesquisa jurídica (artigos, leis, jurisprudência)
    if any(pattern in message_lower for pattern in ["artigo", "art.", "lei", "código", "cpc", "clt", "lgpd", "jurisprudência"]):
        return RouteDecision(
            intent=QueryIntent.PESQUISA_JURIDICA,
            use_agent=False,
            use_rag=True,
            explanation="Pesquisa jurídica - usando RAG + LLM"
        )
    
    # Conversação geral (default)
    return RouteDecision(
        intent=QueryIntent.CONVERSACIONAL,
        use_agent=False,
        use_rag=True,
        explanation="Conversa geral - usando RAG + LLM"
    )


async def route_query(
    message: str,
    escritorio_id: str,
    history: Optional[list] = None
) -> tuple[RouteDecision, str]:
    """
    Rota a query e retorna a decisão + estratégia escolhida.
    
    Returns:
        (RouteDecision, strategy_name)
        strategy_name: "agent" | "chain" | "rag_direct"
    """
    decision = await classify_query_intent(message)
    
    if decision.use_agent:
        return decision, "agent"
    elif decision.use_rag:
        return decision, "chain"
    else:
        return decision, "rag_direct"
