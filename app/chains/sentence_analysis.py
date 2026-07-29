"""Chain para análise de sentenças com RAG (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical


def create_sentence_analysis_chain(escritorio_id: str):
    """
    Chain: Analisa sentenças identificando chances de recurso e pontos fracos.

    Fluxo:
    1. Busca conhecimento relevante (teses, súmulas) no RAG
    2. Envia contexto + sentença para o LLM
    3. Retorna análise estruturada com teses recursais
    """
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("sentence_analysis")

    temperature = prompt_config.get("temperature", 0.1)
    max_tokens = prompt_config.get("max_tokens", 2200)
    template = prompt_config["system_prompt"]

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)

    def get_context(inputs: dict) -> str:
        query = f"recurso teses jurisprudência {inputs.get('sentence_text', '')[:200]}"
        store = get_rag_store()
        result = store.search(escritorio_id, query, limit=3)
        if not result.chunks:
            return "Nenhum conhecimento específico encontrado."
        return "\n\n".join([f"- {c.content}" for c in result.chunks])

    chain = (
        RunnablePassthrough.assign(context=get_context)
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


async def analyze_sentence(escritorio_id: str, sentence_text: str) -> str:
    """Analisa uma sentença e retorna relatório com chances de recurso."""
    chain = create_sentence_analysis_chain(escritorio_id)
    result = await chain.ainvoke({"sentence_text": sentence_text})
    return result
