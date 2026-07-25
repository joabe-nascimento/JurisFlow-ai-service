"""Provedor de LLM — suporta Groq (grátis), Azure OpenAI e OpenAI."""

from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from app.config import settings


def get_llm(temperature: float = 0.0, max_tokens: Optional[int] = None) -> BaseChatModel:
    """
    Retorna o LLM configurado baseado no provider.
    
    Providers suportados:
    - groq: GRÁTIS (Llama 3.3 70B, Mixtral 8x7B) - https://console.groq.com
    - openrouter: GRÁTIS/pago via https://openrouter.ai
    - azure: Azure OpenAI (GPT-4o) - PAGO
    - openai: OpenAI (GPT-4o-mini) - PAGO
    """
    provider = settings.llm_provider.lower()
    
    if provider == "groq":
        if not settings.groq_api_key:
            raise ValueError(
                "groq_api_key não configurada. "
                "Obtenha grátis em https://console.groq.com/keys"
            )
        return ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.groq_model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        )

    elif provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError(
                "openrouter_api_key não configurada. "
                "Obtenha em https://openrouter.ai/keys"
            )
        return ChatOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            default_headers={
                "HTTP-Referer": settings.openrouter_site_url,
                "X-Title": settings.openrouter_site_name,
            },
        )
    
    elif provider == "azure":
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
    
    elif provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("openai_api_key não configurada")
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
        )
    
    else:
        raise ValueError(
            f"Provider '{provider}' não suportado. "
            "Use: groq | openrouter | azure | openai"
        )


def get_provider_info() -> dict:
    """Retorna informações sobre o provider LLM atual."""
    provider = settings.llm_provider.lower()
    
    info = {
        "provider": provider,
        "configured": False,
        "model": "",
        "cost": "",
    }
    
    if provider == "groq":
        info["configured"] = bool(settings.groq_api_key)
        info["model"] = settings.groq_model
        info["cost"] = "GRÁTIS"
    elif provider == "openrouter":
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
