#!/usr/bin/env bash
set -euo pipefail
DIR=/root/autodl-tmp
PIDFILE="$DIR/qwen-novel.pid"
if [[ -f "$PIDFILE" ]]; then
  PID=$(cat "$PIDFILE")
  if [[ "$PID" =~ ^[0-9]+$ ]] && kill -0 "$PID" 2>/dev/null && grep -aq 'llama-server' "/proc/$PID/cmdline"; then
    echo "Qwen already running: $PID"
    exit 0
  fi
fi
if curl -fsS --max-time 3 http://127.0.0.1:8081/health >/dev/null 2>&1; then
  echo 'Port 8081 already serves a healthy model.'
  exit 0
fi
nohup bash "$DIR/run_server_coletti.sh" >> "$DIR/server-novel.log" 2>&1 < /dev/null &
echo $! > "$PIDFILE"
echo "Started Qwen PID $(cat "$PIDFILE")"
