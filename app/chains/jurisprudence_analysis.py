"""Chain para análise de jurisprudência (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical


def create_jurisprudence_chain(escritorio_id: str):
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("jurisprudence_analysis")
    
    temperature = prompt_config.get("temperature", 0.1)
    max_tokens = prompt_config.get("max_tokens", 2000)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)

    def get_context(inputs: dict) -> str:
        query = f"{inputs['tema']} {inputs['area_juridica']} jurisprudência súmula"
        store = get_rag_store()
        result = store.search(escritorio_id, query, limit=3)
        if not result.chunks:
            return "Nenhum conhecimento específico encontrado na base do escritório."
        return "\n\n".join(f"- {c.content}" for c in result.chunks)

    return RunnablePassthrough.assign(context=get_context) | prompt | llm | StrOutputParser()


async def analyze_jurisprudence(escritorio_id: str, tema: str, area_juridica: str) -> str:
    """Analisa teses, jurisprudência e estratégia para um tema jurídico."""
    chain = create_jurisprudence_chain(escritorio_id)
    return await chain.ainvoke({"tema": tema, "area_juridica": area_juridica or "Geral"})
