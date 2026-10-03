#!/usr/bin/env bash
# 常驻看护循环: 每 INTERVAL 秒执行一次关机判定
INTERVAL="${INTERVAL:-60}"
LOG="/root/autodl-tmp/idle_shutdown.log"
echo "[$(date '+%F %T')] watchdog loop started interval=${INTERVAL}s pid=$$" >> "$LOG"
while true; do
  bash /root/autodl-tmp/llm-idle-shutdown.sh
  sleep "$INTERVAL"
done
