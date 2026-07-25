"""Exceções e helpers para chamadas LLM."""


class LLMError(Exception):
    """Erro genérico de LLM."""


class LLMRateLimitError(LLMError):
    """Limite de uso do provedor LLM (ex.: OpenRouter free tier)."""


def is_rate_limit_error(exc: BaseException) -> bool:
    text = str(exc).lower()
    return (
        "429" in text
        or "rate limit" in text
        or "rate_limit" in text
        or "free-models-per-day" in text
    )
