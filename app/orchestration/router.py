"""Router inteligente que decide a melhor estratégia (configurável por vertical)."""

from __future__ import annotations

from typing import Literal, Optional
from enum import Enum
import re

from app.llm.provider import get_llm
from app.verticals.loader import get_current_vertical


class QueryIntent(str, Enum):
    """Tipos de intenção identificados (dinâmico baseado no vertical)."""
    BUSCAR_PROCESSO = "buscar_processo"
    VERIFICAR_PRAZO = "verificar_prazo"
    BUSCAR_CLIENTE = "buscar_cliente"
    CALCULAR_PRAZO = "calcular_prazo"
    PESQUISA_JURIDICA = "pesquisa_juridica"
    CONVERSACIONAL = "conversacional"
    
    @classmethod
    def from_string(cls, intent: str) -> "QueryIntent":
        """Cria um QueryIntent a partir de uma string."""
        try:
            return cls(intent)
        except ValueError:
            return cls.CONVERSACIONAL


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
    Classifica a intenção da pergunta usando configurações do vertical.
    
    Carrega padrões de router.yaml e aplica lógica de detecção.
    """
    vertical = get_current_vertical()
    intents_config = vertical.router_intents
    
    message_lower = message.lower()
    
    # Itera pelos intents configurados no vertical
    for intent_config in intents_config:
        intent_id = intent_config.get("intent", "conversacional")
        keywords = intent_config.get("keywords", [])
        regex_patterns = intent_config.get("regex_patterns", [])
        conditions = intent_config.get("conditions", {})
        use_agent = intent_config.get("use_agent", False)
        use_rag = intent_config.get("use_rag", True)
        explanation = intent_config.get("explanation", f"Detectado intent: {intent_id}")
        is_default = intent_config.get("default", False)
        
        # Se for intent default, guarda para usar se nenhum outro match
        if is_default:
            default_intent = RouteDecision(
                intent=QueryIntent.from_string(intent_id),
                use_agent=use_agent,
                use_rag=use_rag,
                explanation=explanation
            )
            continue
        
        # Verifica keywords
        keywords_match = any(kw in message_lower for kw in keywords) if keywords else False
        
        # Verifica regex patterns
        regex_match = False
        extracted_entities = {}
        for pattern in regex_patterns:
            match = re.search(pattern, message)
            if match:
                regex_match = True
                extracted_entities[f"match_{intent_id}"] = match.group()
                break
        
        # Verifica condições especiais
        conditions_match = True
        if conditions:
            # has_processo_mention
            if "has_processo_mention" in conditions:
                expected = conditions["has_processo_mention"]
                has_processo = "processo" in message_lower or any(c.isdigit() for c in message)
                if has_processo != expected:
                    conditions_match = False
            
            # has_date
            if "has_date" in conditions:
                expected = conditions["has_date"]
                has_date = any(c.isdigit() for c in message)
                if has_date != expected:
                    conditions_match = False
        
        # Se match em keywords OU regex, E condições satisfeitas
        if (keywords_match or regex_match) and conditions_match:
            return RouteDecision(
                intent=QueryIntent.from_string(intent_id),
                use_agent=use_agent,
                use_rag=use_rag,
                explanation=explanation,
                extracted_entities=extracted_entities or None
            )
    
    # Se nenhum intent matched, retorna o default
    return default_intent


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
