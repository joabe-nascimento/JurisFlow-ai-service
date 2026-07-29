#!/bin/bash
# Setup remoto do JurisFlow AI no HostGator (Python 3.9)
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-hostgator.sh
source "$SCRIPT_DIR/lib-hostgator.sh"

cd "$APP_DIR"

echo "[1/6] Preparando ambiente..."
REQ_FILE="requirements-hostgator.txt"
REQ_HASH=""
if [ -f "$REQ_FILE" ]; then
  REQ_HASH="$(md5sum "$REQ_FILE" 2>/dev/null | awk '{print $1}')"
  if [ -z "$REQ_HASH" ]; then
    REQ_HASH="$(sha256sum "$REQ_FILE" 2>/dev/null | awk '{print $1}')"
  fi
fi
REQ_MARKER=".requirements-hostgator.hash"
SKIP_PIP=0
if [ "${FAST_DEPLOY:-0}" = "1" ] && [ -n "$REQ_HASH" ] && [ -f "$REQ_MARKER" ] && [ "$(cat "$REQ_MARKER" 2>/dev/null)" = "$REQ_HASH" ] && [ -x .venv/bin/python ]; then
  SKIP_PIP=1
  echo "FAST_DEPLOY: pip install pulado (requirements inalterados)"
fi

if [ "$SKIP_PIP" = "0" ]; then
  if [ ! -f .venv/bin/python ]; then
    rm -rf .venv
    /usr/bin/virtualenv --copies -p /usr/bin/python3 .venv
  fi

  source .venv/bin/activate
  pip install --upgrade pip wheel setuptools
  pip install -r requirements-hostgator.txt
  if [ -n "$REQ_HASH" ]; then
    echo "$REQ_HASH" > "$REQ_MARKER"
  fi
else
  source .venv/bin/activate
fi

if [ -f .env.hostgator ]; then
  cp .env.hostgator .env
fi

chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
chmod +x "$APP_DIR/watchdog.sh" 2>/dev/null || true

echo "[2/6] Parando instancia anterior..."
jurisflow_stop

echo "[3/6] Iniciando JurisFlow (setsid, desacoplado da sessao SSH)..."
jurisflow_start
sleep 8

echo "[4/6] Verificando health..."
if jurisflow_health_ok; then
  echo "OK: JurisFlow respondendo em 127.0.0.1:$PORT"
  curl -s "http://127.0.0.1:$PORT/health"
else
  echo "ERRO: health check falhou"
  tail -n 50 "$LOG_FILE" || true
  exit 1
fi

echo "[5/6] Instalando cron watchdog (a cada 5 min, com flock)..."
jurisflow_install_cron
echo "Cron atual:"
crontab -l | grep -F "watchdog-hostgator.sh" || true

echo "[6/6] Limpando cache Symfony..."
if [ "${FAST_DEPLOY:-0}" = "1" ]; then
  cd /home2/joabef36/unio-uniojuridico
  php bin/console cache:clear --env=prod --no-warmup 2>/dev/null || true
else
  cd /home2/joabef36/unio-uniojuridico
  php bin/console cache:clear --env=prod --no-warmup 2>/dev/null || true
  php bin/console cache:warmup --env=prod 2>/dev/null || true
fi

echo "Deploy JurisFlow concluido."
