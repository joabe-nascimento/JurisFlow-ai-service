#!/bin/bash
# Constantes e funções compartilhadas para deploy no HostGator.

APP_DIR="/home2/joabef36/jurisflow-ai"
# Portas 8091 e 8092 ficaram com processos zumbis presos em sessoes SSH isoladas
# (CloudLinux jail nao deixa matar de outra sessao, nem por PID, nem por fuser/lsof
# — o processo so aparece via curl na porta, invisivel em ps/kill/fuser). Mudado
# para 8094. Se acontecer de novo, so migrar para outra porta livre (confirmar
# com curl -m3 http://127.0.0.1:PORTA/health antes de reusar qualquer porta antiga).
PORT=8094
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
  # CPU time (ulimit -t) do LVE do HostGator eh limitado a 120s (hard limit,
  # nao pode ser aumentado). O processo uvicorn MORRE periodicamente ao
  # acumular esse tempo de CPU. O watchdog precisa rodar a cada 1 min para
  # minimizar a janela de indisponibilidade quando isso acontece.
  local cron_line="* * * * * flock -n $LOCK_FILE $APP_DIR/scripts/watchdog-hostgator.sh >/dev/null 2>&1"
  local current
  current=$(crontab -l 2>/dev/null || true)

  # Sempre reinstala (remove qualquer entrada antiga do watchdog, mesmo com
  # intervalo diferente) para garantir que o intervalo atual seja aplicado.
  {
    echo "$current" | sed '/watchdog-hostgator\.sh/d' | sed '/watchdog\.sh/d' | sed '/^$/d'
    echo "$cron_line"
  } | crontab -
}
