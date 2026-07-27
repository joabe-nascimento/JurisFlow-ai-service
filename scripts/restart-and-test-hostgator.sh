#!/bin/bash
set -eu
cd /home2/joabef36/jurisflow-ai

echo "=== .env Azure ==="
grep AZURE .env

echo "=== Settings loaded ==="
.venv/bin/python3 - <<'PY'
from app.config import settings
k = settings.azure_openai_key
print("key_prefix", k[:24] if k else "EMPTY")
print("endpoint", settings.azure_openai_endpoint)
print("deployment", settings.azure_deployment_name)
PY

pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 2
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8090 >> jurisflow.log 2>&1 &
sleep 10

.venv/bin/python3 /tmp/test-bruna-remote.py
