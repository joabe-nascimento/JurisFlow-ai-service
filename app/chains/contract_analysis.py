"""Chain para análise de contratos com RAG (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.llm.provider import get_llm
from app.rag.langchain_store import langchain_rag_store
from app.verticals.loader import get_current_vertical


def create_contract_analysis_chain(escritorio_id: str):
    """
    Chain: Analisa contratos buscando cláusulas de risco.
    
    Fluxo:
    1. Busca conhecimento sobre cláusulas de risco no RAG
    2. Envia contexto + contrato para o LLM
    3. Retorna análise estruturada
    """
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("contract_analysis")
    
    temperature = prompt_config.get("temperature", 0.1)
    max_tokens = prompt_config.get("max_tokens", 2000)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)
    
    # Retriever do RAG
    def get_context(inputs: dict) -> str:
        query = f"cláusulas de risco contratos {inputs.get('contract_text', '')[:200]}"
        result = langchain_rag_store.search(escritorio_id, query, limit=3)
        if not result.chunks:
            return "Nenhum conhecimento específico encontrado."
        return "\n\n".join([f"- {c.content}" for c in result.chunks])
    
    # Chain: input → retrieval → prompt → LLM → parse
    chain = (
        RunnablePassthrough.assign(context=get_context)
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain


async def analyze_contract(escritorio_id: str, contract_text: str) -> str:
    """Analisa um contrato e retorna relatório de riscos."""
    chain = create_contract_analysis_chain(escritorio_id)
    result = await chain.ainvoke({"contract_text": contract_text})
    return result
