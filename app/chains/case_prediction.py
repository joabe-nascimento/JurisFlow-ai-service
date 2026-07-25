"""Chain para análise preditiva de resultado (configurável por vertical)."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.verticals.loader import get_current_vertical


def create_case_prediction_chain():
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("case_prediction")
    
    temperature = prompt_config.get("temperature", 0.2)
    max_tokens = prompt_config.get("max_tokens", 2000)
    template = prompt_config["system_prompt"]
    
    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | llm | StrOutputParser()


async def predict_case_outcome(escritorio_id: str, data: dict) -> str:
    """Analisa probabilidade de êxito e estratégia de um processo."""
    chain = create_case_prediction_chain()
    return await chain.ainvoke(data)
