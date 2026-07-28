"""Agente jurídico com tool calling (compatível com GPT-5 / modelos sem parâmetro stop)."""

from typing import Literal, Optional, Sequence

try:
    # LangChain >= 1.0 moveu os agentes clássicos para este pacote separado.
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    # LangChain 0.3.x (usado no HostGator, sem langchain-classic instalado).
    from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.agents.tools import legal_tools
from app.config import settings
from app.llm.provider import get_llm


def create_legal_agent(escritorio_id: str = "default", tools: Optional[Sequence] = None) -> AgentExecutor:
    """
    Cria agente jurídico com tool calling nativo.

    Usa function calling em vez de ReAct para evitar o parâmetro `stop`,
    que não é suportado por modelos GPT-5/o-series no Azure OpenAI.

    Args:
        tools: lista de tools a expor ao agente (default: apenas legal_tools,
            sem acesso a dados reais do escritório — usar sasha_orchestrator
            para incluir as tools de integração escopadas por escritorio_id).
    """
    llm = get_llm(temperature=0.0)
    active_tools = list(tools) if tools is not None else legal_tools

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """Você é a Sasha, assistente jurídica inteligente com acesso a ferramentas especializadas.

Responda à pergunta do advogado da melhor forma possível. Regras:
- SEMPRE use as tools disponíveis quando necessário
- NÃO invente informações — use buscar_conhecimento ou buscar_jurisprudencia
- Para cálculos de prazo, use calcular_prazo
- Para honorários, use calcular_honorarios
- Seja precisa e cite fontes quando aplicável
- Responda em português brasileiro, de forma clara e profissional""",
        ),
        MessagesPlaceholder("chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=llm,
        tools=active_tools,
        prompt=prompt,
    )

    return AgentExecutor(
        agent=agent,
        tools=active_tools,
        verbose=settings.agent_verbose,
        max_iterations=settings.agent_max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


async def run_agent(
    question: str,
    escritorio_id: str = "default",
    mode: Literal["full", "answer_only"] = "full",
    tools: Optional[Sequence] = None,
) -> dict:
    """
    Executa o agente jurídico.

    Args:
        question: Pergunta do advogado
        escritorio_id: ID do escritório (para buscar_conhecimento)
        mode: 'full' retorna steps intermediários, 'answer_only' só resposta final
        tools: lista de tools a expor (ver create_legal_agent)

    Returns:
        Dict com answer, intermediate_steps (se mode='full')
    """
    agent_executor = create_legal_agent(escritorio_id, tools=tools)

    try:
        result = await agent_executor.ainvoke({
            "input": question,
            "chat_history": [],
        })

        if mode == "answer_only":
            return {"answer": result["output"]}

        steps = []
        for step in result.get("intermediate_steps", []):
            action, observation = step
            steps.append({
                "tool": action.tool,
                "input": action.tool_input,
                "output": str(observation)[:500],
            })

        return {
            "answer": result["output"],
            "steps": steps,
            "iterations": len(steps),
        }

    except Exception as e:
        return {
            "answer": f"Erro ao executar agente: {str(e)}",
            "error": True,
        }
