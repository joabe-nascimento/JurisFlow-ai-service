#!/bin/bash
# Setup remoto do JurisFlow AI no HostGator (Python 3.9)
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-hostgator.sh
source "$SCRIPT_DIR/lib-hostgator.sh"

cd "$APP_DIR"

echo "[1/6] Preparando ambiente..."
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
cd /home2/joabef36/unio-uniojuridico
php bin/console cache:clear --env=prod --no-warmup 2>/dev/null || true
php bin/console cache:warmup --env=prod 2>/dev/null || true

echo "Deploy JurisFlow concluido."
