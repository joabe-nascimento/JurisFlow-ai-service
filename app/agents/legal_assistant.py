"""Agente jurídico com ReAct pattern (Reasoning + Acting)."""

from typing import Literal

from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate

from app.agents.tools import legal_tools
from app.config import settings
from app.llm.provider import get_llm


def create_legal_agent(escritorio_id: str = "default") -> AgentExecutor:
    """
    Cria agente jurídico com ReAct pattern.
    
    ReAct = Reasoning (raciocínio) + Acting (ação com tools).
    
    O agente:
    1. Recebe uma pergunta
    2. Raciocina sobre qual tool usar
    3. Executa a tool
    4. Analisa o resultado
    5. Decide se precisa de mais tools ou pode responder
    6. Retorna resposta final
    
    Tools disponíveis:
    - calcular_prazo: Calcula prazos processuais
    - buscar_conhecimento: Busca na base RAG
    - buscar_jurisprudencia: Busca jurisprudência (simulado)
    - calcular_honorarios: Calcula honorários OAB
    """
    
    llm = get_llm(temperature=0.0)
    
    # Prompt ReAct padrão LangChain
    react_prompt = PromptTemplate.from_template(
        """Você é um assistente jurídico inteligente com acesso a ferramentas especializadas.

Responda à pergunta do advogado da melhor forma possível. Você tem acesso às seguintes ferramentas:

{tools}

Use o seguinte formato:

Pergunta: a pergunta que você deve responder
Pensamento: você deve sempre pensar sobre o que fazer
Ação: a ação a tomar, deve ser uma de [{tool_names}]
Entrada da Ação: a entrada para a ação
Observação: o resultado da ação
... (este Pensamento/Ação/Entrada da Ação/Observação pode se repetir N vezes)
Pensamento: Agora sei a resposta final
Resposta Final: a resposta final para a pergunta original

Importante:
- SEMPRE use as tools disponíveis quando necessário
- NÃO invente informações - use buscar_conhecimento ou buscar_jurisprudencia
- Para cálculos de prazo, use calcular_prazo
- Para honorários, use calcular_honorarios
- Seja preciso e cite fontes

Comece agora!

Pergunta: {input}
Pensamento: {agent_scratchpad}"""
    )
    
    agent = create_react_agent(
        llm=llm,
        tools=legal_tools,
        prompt=react_prompt,
    )
    
    agent_executor = AgentExecutor(
        agent=agent,
        tools=legal_tools,
        verbose=settings.agent_verbose,
        max_iterations=settings.agent_max_iterations,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    
    return agent_executor


async def run_agent(
    question: str,
    escritorio_id: str = "default",
    mode: Literal["full", "answer_only"] = "full"
) -> dict:
    """
    Executa o agente jurídico.
    
    Args:
        question: Pergunta do advogado
        escritorio_id: ID do escritório (para buscar_conhecimento)
        mode: 'full' retorna steps intermediários, 'answer_only' só resposta final
    
    Returns:
        Dict com answer, intermediate_steps (se mode='full')
    """
    agent_executor = create_legal_agent(escritorio_id)
    
    try:
        result = await agent_executor.ainvoke({"input": question})
        
        if mode == "answer_only":
            return {"answer": result["output"]}
        
        # Formata steps para resposta
        steps = []
        for step in result.get("intermediate_steps", []):
            action, observation = step
            steps.append({
                "tool": action.tool,
                "input": action.tool_input,
                "output": str(observation)[:500],  # Limita tamanho
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
