#!/bin/bash
# Watchdog: verifica /health e reinicia se necessario.
# Executado via cron a cada 5 min (com flock para evitar concorrencia).
set -eu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-hostgator.sh
source "$SCRIPT_DIR/lib-hostgator.sh"

cd "$APP_DIR" || exit 1

if jurisflow_health_ok; then
  exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - JurisFlow OFFLINE (porta $PORT), reiniciando..." >> "$WATCHDOG_LOG"

jurisflow_stop
jurisflow_start
sleep 8

if jurisflow_health_ok; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - JurisFlow reiniciado com sucesso (PID $(cat "$PID_FILE" 2>/dev/null || echo '?'))." >> "$WATCHDOG_LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') - FALHA ao reiniciar JurisFlow." >> "$WATCHDOG_LOG"
  tail -n 20 "$LOG_FILE" >> "$WATCHDOG_LOG" 2>/dev/null || true
  exit 1
fi
