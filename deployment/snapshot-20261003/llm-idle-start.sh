#!/usr/bin/env bash
# 单实例拉起常驻看护(幂等)
PIDF="/var/tmp/llm-idle-watchdog.pid"
if [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; then
  echo "watchdog already running pid=$(cat "$PIDF")"
  exit 0
fi
nohup bash /root/autodl-tmp/llm-idle-watchdog.sh >> /root/autodl-tmp/idle_shutdown.log 2>&1 &
echo $! > "$PIDF"
echo "started watchdog pid=$!"
