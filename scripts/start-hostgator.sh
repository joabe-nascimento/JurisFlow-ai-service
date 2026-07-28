#!/bin/bash
# Inicia o JurisFlow AI desacoplado da sessao SSH (setsid).
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-hostgator.sh
source "$SCRIPT_DIR/lib-hostgator.sh"

if jurisflow_health_ok; then
  echo "JurisFlow ja esta online em 127.0.0.1:$PORT"
  curl -s "http://127.0.0.1:$PORT/health"
  exit 0
fi

jurisflow_stop
jurisflow_start
sleep 8

if jurisflow_health_ok; then
  echo "OK: JurisFlow iniciado em 127.0.0.1:$PORT (PID $(cat "$PID_FILE"))"
  curl -s "http://127.0.0.1:$PORT/health"
  exit 0
fi

echo "ERRO: health check falhou apos start" >&2
tail -n 40 "$LOG_FILE" >&2 || true
exit 1
