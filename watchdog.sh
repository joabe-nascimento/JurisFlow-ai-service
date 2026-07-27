#!/bin/bash
APP_DIR="/home2/joabef36/jurisflow-ai"
PORT=8093
LOG_FILE="$APP_DIR/jurisflow-$PORT.log"
WATCHDOG_LOG="$APP_DIR/watchdog.log"

cd "$APP_DIR" || exit 1

if curl -sf -m 5 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
  exit 0
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') - JurisFlow OFFLINE (porta $PORT), reiniciando..." >> "$WATCHDOG_LOG"
pkill -f "uvicorn app.main:app" 2>/dev/null
sleep 2
cp -f .env.hostgator .env 2>/dev/null
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT" < /dev/null >> "$LOG_FILE" 2>&1 &
disown
sleep 8

if curl -sf -m 5 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1; then
  echo "$(date '+%Y-%m-%d %H:%M:%S') - JurisFlow reiniciado com sucesso (porta $PORT)." >> "$WATCHDOG_LOG"
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') - FALHA ao reiniciar JurisFlow (porta $PORT)." >> "$WATCHDOG_LOG"
fi
