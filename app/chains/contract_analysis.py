"""Chain para análise de contratos com RAG."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

from app.llm.provider import get_llm
from app.rag.langchain_store import langchain_rag_store


def create_contract_analysis_chain(escritorio_id: str):
    """
    Chain: Analisa contratos buscando cláusulas de risco.
    
    Fluxo:
    1. Busca conhecimento sobre cláusulas de risco no RAG
    2. Envia contexto + contrato para o LLM
    3. Retorna análise estruturada
    """
    
    llm = get_llm(temperature=0.0)
    
    template = """Você é um advogado especialista em análise de contratos.

Sua tarefa: analisar o contrato fornecido e identificar cláusulas de risco com base no conhecimento jurídico disponível.

## Conhecimento Jurídico (RAG):
{context}

## Contrato para Análise:
{contract}

## Instruções:
1. Identifique cláusulas de risco (limitação de responsabilidade, multas, foro, cessão de IP, rescisão)
2. Classifique cada risco como: ALTO | MÉDIO | BAIXO
3. Sugira ajustes para mitigar riscos
4. Cite artigos de lei quando aplicável

## Formato de Resposta:
**RESUMO EXECUTIVO:**
[resumo em 2-3 linhas]

**CLÁUSULAS DE RISCO IDENTIFICADAS:**

1. [Título da Cláusula] - Risco: [ALTO/MÉDIO/BAIXO]
   - Texto: "[trecho da cláusula]"
   - Problema: [explicação do risco]
   - Sugestão: [como ajustar]
   - Fundamento: [artigo de lei, se aplicável]

[repetir para cada risco]

**RECOMENDAÇÕES FINAIS:**
[orientações gerais]

---
Resposta:"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Retriever do RAG
    def get_context(inputs: dict) -> str:
        query = f"cláusulas de risco contratos {inputs.get('contract', '')[:200]}"
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
    result = await chain.ainvoke({"contract": contract_text})
    return result
