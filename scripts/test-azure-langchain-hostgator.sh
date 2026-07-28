#!/bin/bash
set -eu
cd /home2/joabef36/jurisflow-ai
source .venv/bin/activate

python3 - <<'PY'
from app.config import settings
from langchain_openai import AzureChatOpenAI
from app.llm.provider import _azure_temperature, _azure_token_kwargs

llm = AzureChatOpenAI(
    azure_endpoint=settings.azure_openai_endpoint,
    api_key=settings.azure_openai_key,
    deployment_name=settings.azure_deployment_name,
    temperature=_azure_temperature(0.4),
    api_version="2024-12-01-preview",
    **_azure_token_kwargs(1024),
)
print("key_prefix", settings.azure_openai_key[:12])
print(llm.invoke("Ola, bom dia").content[:300])
PY

pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8090 >> jurisflow.log 2>&1 &
sleep 10
python3 /tmp/test-bruna-remote.py
