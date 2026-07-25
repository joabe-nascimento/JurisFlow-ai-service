# ═══════════════════════════════════════════════════════════════════════════
# JURISFLOW AI SERVICE - DOCKERFILE
# ═══════════════════════════════════════════════════════════════════════════

FROM python:3.11-slim

WORKDIR /app

# Dependências de sistema necessárias para FAISS/sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python primeiro (aproveita cache de camadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY app ./app

# Usuário não-root
RUN useradd --create-home --shell /bin/bash jurisflow \
    && chown -R jurisflow:jurisflow /app
USER jurisflow

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8090/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
