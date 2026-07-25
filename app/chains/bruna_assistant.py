"""Bruna — assistente jurídica conversacional com RAG + LLM."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.langchain_store import langchain_rag_store

BRUNA_TEMPLATE = """Você é Bruna, assistente jurídica do JurisFlow. Responda de forma natural e conversacional, como uma advogada experiente conversando com um colega.

BASE DE CONHECIMENTO:
{context}

HISTÓRICO DA CONVERSA:
{history}

PERGUNTA ATUAL:
{message}

EXEMPLO DE RESPOSTA IDEAL (use como referência de tom e estilo):
"Sim, o prazo para contestar é de 15 dias úteis, conforme o art. 335 do CPC. Esse prazo começa a contar da audiência de conciliação (se não houver acordo) ou da citação. Se tiver mais de um réu com advogados diferentes, o prazo é em dobro. Qualquer dúvida sobre como calcular, é só falar."

INSTRUÇÕES CRÍTICAS:
- NUNCA use listas com bullets (*, -, •) ou numeradas
- NUNCA use subtítulos ou seções
- NUNCA use negritos excessivos (máximo 2 palavras em toda a resposta)
- Escreva em parágrafos corridos e naturais
- Cite leis de forma fluida no texto
- Se já conversou antes, não se apresente novamente
- Seja breve (2-3 parágrafos pequenos)
- Termine convidando para mais perguntas

RESPONDA AGORA:"""


def _format_history(history: list | None) -> str:
    if not history:
        return "Sem histórico anterior."
    lines = []
    for msg in history[-6:]:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            label = "Advogado" if role == "user" else "Bruna"
            content = (msg.get("content") or "")[:800]
            lines.append(f"{label}: {content}")
    return "\n".join(lines)


def _retrieve_context(escritorio_id: str, message: str, use_rag: bool) -> str:
    if not use_rag:
        return "RAG desabilitado para esta conversa."
    result = langchain_rag_store.search(escritorio_id, message, limit=4)
    if not result.chunks:
        langchain_rag_store.seed_defaults(escritorio_id)
        result = langchain_rag_store.search(escritorio_id, message, limit=4)
    if not result.chunks:
        return "Nenhum documento relevante na base do escritório."
    return "\n\n---\n\n".join(
        f"**{c.document_title}** ({c.category})\n{c.content}"
        for c in result.chunks
    )


async def bruna_chat(
    escritorio_id: str,
    message: str,
    use_rag: bool = True,
    history: list | None = None,
) -> str:
    """Chat conversacional com Bruna (1 chamada LLM + RAG)."""
    llm = get_llm(temperature=0.4, max_tokens=1024)
    prompt = ChatPromptTemplate.from_template(BRUNA_TEMPLATE)

    def prepare(inputs: dict) -> dict:
        return {
            "message": inputs["message"],
            "context": _retrieve_context(
                inputs["escritorio_id"], inputs["message"], inputs["use_rag"]
            ),
            "history": _format_history(inputs.get("history")),
        }

    chain = prepare | prompt | llm | StrOutputParser()
    return await chain.ainvoke(
        {
            "message": message,
            "escritorio_id": escritorio_id,
            "use_rag": use_rag,
            "history": history,
        }
    )
