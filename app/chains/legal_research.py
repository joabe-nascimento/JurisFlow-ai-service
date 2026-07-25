"""Chain para pesquisa jurídica com RAG."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.langchain_store import langchain_rag_store


def create_legal_research_chain(escritorio_id: str):
    """
    Chain: Pesquisa jurídica com RAG.
    
    Fluxo:
    1. Busca no RAG documentos relevantes
    2. Sintetiza resposta baseada no contexto
    3. Retorna com fontes citadas
    """
    
    llm = get_llm(temperature=0.1)
    
    template = """Você é um assistente jurídico de pesquisa.

## Pergunta do Advogado:
{question}

## Base de Conhecimento (RAG):
{context}

## Instruções:
1. Responda a pergunta com base APENAS no conhecimento fornecido
2. Cite as fontes (título do documento, artigo de lei)
3. Se não houver informação suficiente, diga "Informação não encontrada na base"
4. Seja objetivo e preciso

## Formato de Resposta:
**RESPOSTA:**
[resposta objetiva]

**FUNDAMENTO LEGAL:**
[artigos, leis, precedentes citados]

**FONTES CONSULTADAS:**
- [Fonte 1]
- [Fonte 2]

---
Resposta:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def format_context(inputs: dict) -> dict:
        question = inputs["question"]
        result = langchain_rag_store.search(escritorio_id, question, limit=5)
        
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
