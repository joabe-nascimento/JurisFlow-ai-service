from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "JurisFlow AI Service"
    host: str = "0.0.0.0"
    port: int = 8090
    
    # LLM Provider (openrouter = grátis/pago, azure = pago, openai = pago)
    llm_provider: str = "openrouter"  # openrouter | azure | openai

    # Azure OpenAI (PAGO - para produção)
    azure_openai_key: str = ""
    azure_openai_endpoint: str = ""
    azure_deployment_name: str = "gpt-4o"
    
    # OpenAI (PAGO - alternativa)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # OpenRouter (GRÁTIS com modelos free + opção paga)
    openrouter_api_key: str = ""
    openrouter_model: str = "openrouter/free"
    openrouter_fallback_models: str = (
        "meta-llama/llama-3.2-3b-instruct:free,"
        "qwen/qwen-2.5-7b-instruct:free,"
        "google/gemma-2-9b-it:free"
    )
    openrouter_site_url: str = "http://localhost:3000"
    openrouter_site_name: str = "JurisFlow"
    
    # RAG & Embeddings
    retrieval_method: str = "langchain"  # langchain | tfidf | lexical
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Local, gratuito
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    
    # Agent
    agent_enabled: bool = True
    agent_max_iterations: int = 10
    agent_verbose: bool = True
    
    # Java API Integration
    java_api_url: str = "http://localhost:8082/api"

    # Segredo compartilhado enviado no header X-Internal-Secret ao chamar a API
    # interna do backend (ex.: Unio Jurídico /api/v1/interno). Deve bater com
    # LEGAL_AI_INTERNAL_SECRET configurado no Symfony.
    legal_api_secret: str = ""
    
    # Vertical (nicho/domínio) — define qual configuração carregar
    ai_vertical: str = "legal"  # legal | medical | financial | etc

    # CORS — lista separada por vírgula de origens permitidas
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:8082"

    # Rate limiting (em memória, por IP — ver app/middleware/rate_limit.py)
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Cada vertical define suas próprias env vars de integração (ex.:
        # LEGAL_API_URL, MEDICAL_API_URL — ver VerticalConfig.integration_api_url).
        # Sem "ignore" aqui, qualquer uma dessas variáveis extras no .env quebra
        # a inicialização do Settings global com "extra_forbidden".
        extra = "ignore"


settings = Settings()
