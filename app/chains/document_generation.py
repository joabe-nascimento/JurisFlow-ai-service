"""Chain para geração de documentos jurídicos (petições, contratos)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.langchain_store import langchain_rag_store


def create_document_generation_chain(escritorio_id: str):
    """
    Chain: Gera minutas de documentos jurídicos.
    
    Fluxo:
    1. Busca templates/exemplos no RAG
    2. Gera documento baseado nos dados fornecidos
    3. Retorna minuta completa
    """
    
    llm = get_llm(temperature=0.3)  # Um pouco de criatividade
    
    template = """Você é um advogado redator de documentos jurídicos.

## Tipo de Documento:
{document_type}

## Dados Fornecidos:
{data}

## Referências (RAG):
{context}

## Instruções:
1. Gere uma minuta profissional do documento solicitado
2. Use linguagem técnica apropriada
3. Inclua todas as cláusulas necessárias
4. Deixe campos editáveis entre [colchetes] quando dados específicos faltarem
5. Siga formato padrão brasileiro

## Formato de Resposta:
[Documento completo formatado]

---
Documento:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    def prepare_inputs(inputs: dict) -> dict:
        doc_type = inputs["document_type"]
        data = inputs["data"]
        
        # Busca exemplos/templates no RAG
        query = f"{doc_type} modelo template cláusulas"
        result = langchain_rag_store.search(escritorio_id, query, limit=2)
        
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
