"""Chain para comparação de dois documentos jurídicos (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical


def create_document_comparison_chain(escritorio_id: str):
    """
    Chain: Compara dois documentos jurídicos e destaca diferenças relevantes.

    Fluxo:
    1. Busca conhecimento relevante no RAG (opcional, contexto geral)
    2. Envia os dois documentos para o LLM
    3. Retorna comparação estruturada
    """
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("document_comparison")

    temperature = prompt_config.get("temperature", 0.1)
    max_tokens = prompt_config.get("max_tokens", 2200)
    template = prompt_config["system_prompt"]

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)

    def get_context(inputs: dict) -> str:
        query = f"comparação de documentos {inputs.get('document_a', '')[:150]}"
        store = get_rag_store()
        result = store.search(escritorio_id, query, limit=2)
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


async def compare_documents(escritorio_id: str, document_a: str, document_b: str) -> str:
    """Compara dois documentos e retorna relatório de diferenças."""
    chain = create_document_comparison_chain(escritorio_id)
    result = await chain.ainvoke({"document_a": document_a, "document_b": document_b})
    return result
