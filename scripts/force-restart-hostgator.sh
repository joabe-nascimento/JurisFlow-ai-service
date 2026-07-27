#!/bin/bash
set -eu
APP_DIR="/home2/joabef36/jurisflow-ai"
PORT=8090
cd "$APP_DIR"

cp -f .env.hostgator .env

echo "=== Matando processos na porta $PORT ==="
for pid in $(ps aux | grep '[u]vicorn app.main:app' | awk '{print $2}'); do
  kill -9 "$pid" 2>/dev/null || true
done
sleep 2

if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" 2>/dev/null || true
  sleep 2
fi

echo "=== Iniciando JurisFlow ==="
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT" >> jurisflow.log 2>&1 &
sleep 10

echo "=== Processos uvicorn ==="
ps aux | grep '[u]vicorn app.main:app' || echo "NENHUM"

echo "=== Teste Bruna ==="
source .venv/bin/activate
python3 /tmp/test-bruna-remote.py
