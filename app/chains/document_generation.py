"""Chain para geração de documentos (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical


def create_document_generation_chain(escritorio_id: str):
    """
    Chain: Gera minutas de documentos.
    
    Fluxo:
    1. Busca templates/exemplos no RAG
    2. Gera documento baseado nos dados fornecidos
    3. Retorna minuta completa
    """
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("document_generation")
    
    temperature = prompt_config.get("temperature", 0.3)
    max_tokens = prompt_config.get("max_tokens", 3000)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)
    
    def prepare_inputs(inputs: dict) -> dict:
        doc_type = inputs["document_type"]
        data = inputs["data"]
        
        # Busca exemplos/templates no RAG
        query = f"{doc_type} modelo template cláusulas"
        store = get_rag_store()
        result = store.search(escritorio_id, query, limit=2)
        
        context = "Nenhum template encontrado. Gere com base nas boas práticas."
        if result.chunks:
            context = "\n\n".join([c.content for c in result.chunks])
        
        return {
            "document_type": doc_type,
            "data": data,
            "context": context,
        }
    
    chain = prepare_inputs | prompt | llm | StrOutputParser()
    
    return chain


async def generate_document(
    escritorio_id: str,
    document_type: str,
    data: str
) -> str:
    """Gera documento jurídico baseado em tipo e dados."""
    chain = create_document_generation_chain(escritorio_id)
    result = await chain.ainvoke({
        "document_type": document_type,
        "data": data,
    })
    return result
