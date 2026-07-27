"""Validação de respostas do LLM — evita vazar metadados de safety para o usuário."""

import re

# Padrões típicos de modelos free que retornam classificação em vez de resposta
_SAFETY_ONLY_PATTERNS = [
    re.compile(r"^user safety:\s*(safe|unsafe)\s*$", re.I),
    re.compile(r"^safety categories?:.*$", re.I),
    re.compile(r"^content(?:\s+policy)?:\s*(safe|unsafe)\s*$", re.I),
    re.compile(r"^moderation:\s*(pass|fail).*$", re.I),
]


def is_invalid_assistant_response(text: str | None) -> bool:
    """
    Detecta respostas inválidas (metadados de safety, vazias ou sem conteúdo útil).
    Usado para acionar retry com outro modelo/provider.
    """
    if not text or not text.strip():
        return True

    stripped = text.strip()
    lower = stripped.lower()

    # Modelo retornou classificação de safety em vez de resposta
    if lower.startswith("user safety:"):
        return True

    if "safety categories:" in lower and len(stripped) < 220:
        return True

    if "unauthorized advice" in lower and len(stripped) < 220:
        return True

    # Resposta curta que é só classificação de safety
    if len(stripped) < 160:
        if "user safety" in lower:
            return True
        if "safety categories" in lower:
            return True
        if lower in {"safe", "unsafe"}:
            return True

    for pattern in _SAFETY_ONLY_PATTERNS:
        if pattern.match(stripped):
            return True

    return False
