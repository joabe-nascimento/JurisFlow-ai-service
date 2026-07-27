#!/bin/bash
# Setup remoto do JurisFlow AI no HostGator (Python 3.9)
set -eu

APP_DIR="/home2/joabef36/jurisflow-ai"
PORT=8091
LOG_FILE="$APP_DIR/jurisflow.log"
PID_FILE="$APP_DIR/jurisflow.pid"

cd "$APP_DIR"

echo "[1/5] Preparando ambiente..."
if [ ! -f .venv/bin/python ]; then
  rm -rf .venv
  /usr/bin/virtualenv --copies -p /usr/bin/python3 .venv
fi

source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements-hostgator.txt

if [ -f .env.hostgator ]; then
  cp .env.hostgator .env
fi

echo "[2/5] Parando instancia anterior..."
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE" 2>/dev/null || true)
  if [ -n "${OLD_PID:-}" ] && kill -0 "$OLD_PID" 2>/dev/null; then
    kill "$OLD_PID" || true
    sleep 2
  fi
fi
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port $PORT" 2>/dev/null || true
sleep 1

echo "[3/5] Iniciando JurisFlow na porta $PORT..."
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT" > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"
sleep 8

echo "[4/5] Verificando health..."
if curl -sf "http://127.0.0.1:$PORT/health" >/dev/null; then
  echo "OK: JurisFlow respondendo em 127.0.0.1:$PORT"
  curl -s "http://127.0.0.1:$PORT/health"
else
  echo "ERRO: health check falhou"
  tail -n 50 "$LOG_FILE" || true
  exit 1
fi

echo "[5/5] Limpando cache Symfony..."
cd /home2/joabef36/unio-uniojuridico
php bin/console cache:clear --env=prod --no-warmup 2>/dev/null || true
php bin/console cache:warmup --env=prod 2>/dev/null || true

echo "Deploy JurisFlow concluido."
