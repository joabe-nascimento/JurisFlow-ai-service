"""Chain para pesquisa com RAG (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical


def create_legal_research_chain(escritorio_id: str):
    """
    Chain: Pesquisa com RAG.
    
    Fluxo:
    1. Busca no RAG documentos relevantes
    2. Sintetiza resposta baseada no contexto
    3. Retorna com fontes citadas
    """
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("legal_research")
    
    temperature = prompt_config.get("temperature", 0.2)
    max_tokens = prompt_config.get("max_tokens", 1500)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_context(inputs: dict) -> dict:
        question = inputs["question"]
        store = get_rag_store()
        result = store.search(escritorio_id, question, limit=5)
        
        if not result.chunks:
            context = "Nenhum documento relevante encontrado na base de conhecimento."
        else:
            context = "\n\n---\n\n".join([
                f"**{c.document_title}** (Categoria: {c.category})\n{c.content}"
                for c in result.chunks
            ])
        
        return {"question": question, "context": context}
    
    chain = format_context | prompt | llm | StrOutputParser()
    
    return chain


async def research(escritorio_id: str, question: str) -> str:
    """Realiza pesquisa jurídica e retorna resposta fundamentada."""
    chain = create_legal_research_chain(escritorio_id)
    result = await chain.ainvoke({"question": question})
    return result
