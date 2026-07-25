"""Chain para resumo de documentos (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.verticals.loader import get_current_vertical


def create_document_summary_chain():
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("document_summary")
    
    temperature = prompt_config.get("temperature", 0.1)
    max_tokens = prompt_config.get("max_tokens", 1500)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | llm | StrOutputParser()


async def summarize_document(escritorio_id: str, text: str) -> str:
    """Resume um documento/peça processual."""
    chain = create_document_summary_chain()
    return await chain.ainvoke({"text": text})
