"""Provedor de LLM — suporta OpenRouter, Azure OpenAI e OpenAI."""

from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.config import settings


def get_openrouter_model_list() -> list[str]:
    """Modelos OpenRouter em ordem de tentativa (router + fallbacks)."""
    models: list[str] = []
    if settings.openrouter_model:
        models.append(settings.openrouter_model.strip())
    if settings.openrouter_fallback_models:
        for item in settings.openrouter_fallback_models.split(","):
            item = item.strip()
            if item and item not in models:
                models.append(item)
    return models or ["openrouter/free"]


def get_llm_by_provider(
    provider: str,
    temperature: float = 0.0,
    max_tokens: Optional[int] = None,
    model: Optional[str] = None,
) -> BaseChatModel:
    """Instancia LLM para um provider específico."""
    provider = provider.lower()

    if provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError(
                "openrouter_api_key não configurada. "
                "Obtenha em https://openrouter.ai/keys"
            )
        model_id = model or settings.openrouter_model
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            model=model_id,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            default_headers={
                "HTTP-Referer": settings.openrouter_site_url,
                "X-Title": settings.openrouter_site_name,
            },
        )

    if provider == "azure":
        if not settings.azure_openai_key or not settings.azure_openai_endpoint:
            raise ValueError("Azure OpenAI não configurado (chave ou endpoint faltando)")
        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            deployment_name=settings.azure_deployment_name,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            api_version="2024-02-15-preview",
        )

    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("openai_api_key não configurada")
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        )

    raise ValueError(
        f"Provider '{provider}' não suportado. "
        "Use: openrouter | azure | openai"
    )


def get_llm(temperature: float = 0.0, max_tokens: Optional[int] = None) -> BaseChatModel:
    """Retorna o LLM configurado em LLM_PROVIDER."""
    return get_llm_by_provider(settings.llm_provider, temperature, max_tokens)


def get_provider_attempt_order() -> list[str]:
    """Ordem de providers para tentativa com fallback (ex.: OpenRouter → Azure)."""
    primary = settings.llm_provider.lower()
    order: list[str] = [primary]
    if settings.azure_openai_key and settings.azure_openai_endpoint and primary != "azure":
        order.append("azure")
    elif settings.openai_api_key and primary != "openai":
        order.append("openai")
    return order


def get_provider_info() -> dict:
    """Retorna informações sobre o provider LLM atual."""
    provider = settings.llm_provider.lower()

    info = {
        "provider": provider,
        "configured": False,
        "model": "",
        "cost": "",
        "fallback_azure": bool(settings.azure_openai_key and settings.azure_openai_endpoint),
    }

    if provider == "openrouter":
        info["configured"] = bool(settings.openrouter_api_key)
        info["model"] = settings.openrouter_model
        info["cost"] = "Grátis (modelos :free) ou pago"
    elif provider == "azure":
        info["configured"] = bool(settings.azure_openai_key and settings.azure_openai_endpoint)
        info["model"] = settings.azure_deployment_name
        info["cost"] = "Pago (Azure)"
    elif provider == "openai":
        info["configured"] = bool(settings.openai_api_key)
        info["model"] = settings.openai_model
        info["cost"] = "Pago (OpenAI)"

    return info
