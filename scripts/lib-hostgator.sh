#!/bin/bash
# Constantes e funções compartilhadas para deploy no HostGator.

APP_DIR="/home2/joabef36/jurisflow-ai"
PORT=8091
LOG_FILE="$APP_DIR/jurisflow.log"
PID_FILE="$APP_DIR/jurisflow.pid"
WATCHDOG_LOG="$APP_DIR/watchdog.log"
LOCK_FILE="$APP_DIR/.watchdog.lock"
UVICORN_CMD=".venv/bin/uvicorn app.main:app --host 0.0.0.0 --port $PORT"

jurisflow_health_ok() {
  curl -sf -m 5 "http://127.0.0.1:$PORT/health" >/dev/null 2>&1
}

jurisflow_stop() {
  if [ -f "$PID_FILE" ]; then
    local old_pid
    old_pid=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -n "${old_pid:-}" ] && kill -0 "$old_pid" 2>/dev/null; then
      kill "$old_pid" 2>/dev/null || true
      sleep 2
      kill -0 "$old_pid" 2>/dev/null && kill -9 "$old_pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
  fi

  pkill -f "uvicorn app.main:app --host 0.0.0.0 --port $PORT" 2>/dev/null || true
  sleep 1
}

jurisflow_start() {
  cd "$APP_DIR" || return 1

  if [ -f .env.hostgator ]; then
    cp -f .env.hostgator .env
  fi

  if [ ! -x .venv/bin/uvicorn ]; then
    echo "ERRO: .venv/bin/uvicorn nao encontrado em $APP_DIR" >&2
    return 1
  fi

  # setsid desacopla o processo da sessao SSH (evita morte ao fechar conexao).
  setsid .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$PORT" \
    < /dev/null >> "$LOG_FILE" 2>&1 &
  local pid=$!
  echo "$pid" > "$PID_FILE"
  disown "$pid" 2>/dev/null || true
}

jurisflow_install_cron() {
  local cron_line="*/5 * * * * flock -n $LOCK_FILE $APP_DIR/scripts/watchdog-hostgator.sh >/dev/null 2>&1"
  local current
  current=$(crontab -l 2>/dev/null || true)

  if echo "$current" | grep -Fq "watchdog-hostgator.sh"; then
    return 0
  fi

  {
    echo "$current" | sed '/watchdog\.sh/d' | sed '/^$/d'
    echo "$cron_line"
  } | crontab -
}
