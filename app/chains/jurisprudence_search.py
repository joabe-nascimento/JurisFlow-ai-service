"""Chain de pesquisa jurisprudencial estruturada (JSON) com resumos e citações.

Diferente de `jurisprudence_analysis` (texto livre de teses/estratégia), esta
chain retorna uma lista estruturada de julgados/teses prontos para alimentar
a biblioteca de jurisprudência do escritório (Unio Jurídico) com um clique.
"""

from __future__ import annotations

import json
import re

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.llm.provider import get_llm
from app.rag.factory import get_rag_store
from app.verticals.loader import get_current_vertical

RELEVANCIAS_VALIDAS = {"alta", "media", "baixa"}


def _extract_json(raw: str) -> dict:
    """Extrai o primeiro objeto JSON válido de uma resposta do LLM.

    Modelos de chat às vezes envolvem o JSON em blocos ```json ... ``` ou
    acrescentam texto explicativo — aqui isolamos apenas o objeto `{...}`.
    """
    text = raw.strip()
    text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    candidate = match.group(0) if match else text

    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return {"resultados": [], "disclaimer": ""}

    return data if isinstance(data, dict) else {"resultados": [], "disclaimer": ""}


def _sanitize_resultados(data: dict) -> list[dict]:
    resultados = data.get("resultados")
    if not isinstance(resultados, list):
        return []

    sanitized: list[dict] = []
    for item in resultados:
        if not isinstance(item, dict):
            continue

        relevancia = str(item.get("relevancia", "media")).strip().lower()
        if relevancia not in RELEVANCIAS_VALIDAS:
            relevancia = "media"

        tribunal = str(item.get("tribunal", "")).strip()
        tema = str(item.get("tema", "")).strip()
        if not tribunal or not tema:
            continue

        sanitized.append({
            "tribunal": tribunal[:40],
            "tema": tema[:220],
            "resultado": str(item.get("resultado", "")).strip()[:120] or None,
            "relevancia": relevancia,
            "referencia": str(item.get("referencia", "")).strip()[:120] or None,
            "resumo": str(item.get("resumo", "")).strip() or None,
        })

    return sanitized


def create_jurisprudence_search_chain(escritorio_id: str):
    vertical = get_current_vertical()
    prompt_config = vertical.load_prompt("jurisprudence_search")

    temperature = prompt_config.get("temperature", 0.2)
    # GPT-5-mini (reasoning) consome parte do orçamento em tokens de raciocínio
    # ocultos antes de gerar o JSON visível — um valor baixo aqui esgota o
    # orçamento só no raciocínio e devolve conteúdo vazio (finish_reason=length).
    max_tokens = prompt_config.get("max_tokens", 6000)
    template = prompt_config["system_prompt"]

    llm = get_llm(temperature=temperature, max_tokens=max_tokens)
    prompt = ChatPromptTemplate.from_template(template)

    def with_context(inputs: dict) -> dict:
        query = f"{inputs['tema']} {inputs['tribunal']} jurisprudência súmula"
        store = get_rag_store()
        result = store.search(escritorio_id, query, limit=3)
        context = (
            "Nenhum conhecimento específico encontrado na base do escritório."
            if not result.chunks
            else "\n\n".join(f"- {c.content}" for c in result.chunks)
        )
        return {**inputs, "context": context}

    return with_context | prompt | llm | StrOutputParser()


async def search_jurisprudence(
    escritorio_id: str,
    tema: str,
    tribunal: str = "Todos",
    periodo: str = "",
    area_juridica: str = "Geral",
) -> dict:
    """Pesquisa jurisprudência e retorna uma lista estruturada de resultados."""
    chain = create_jurisprudence_search_chain(escritorio_id)
    raw = await chain.ainvoke({
        "tema": tema,
        "tribunal": tribunal or "Todos",
        "periodo": periodo or "não especificado",
        "area_juridica": area_juridica or "Geral",
    })

    data = _extract_json(raw)
    resultados = _sanitize_resultados(data)
    disclaimer = str(data.get("disclaimer") or (
        "Resultados gerados por IA a partir de conhecimento jurídico geral — "
        "confirme sempre a íntegra no site oficial do tribunal antes de citar em peças."
    ))

    return {"resultados": resultados, "disclaimer": disclaimer}
