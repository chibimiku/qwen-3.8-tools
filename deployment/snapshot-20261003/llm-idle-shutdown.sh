#!/usr/bin/env bash
# =============================================================================
#  llm-idle-shutdown.sh  ——  大模型服务器“1 小时空闲自动关机”看护脚本
#  适用: 按小时计费、前面挂 nginx(本机 8080) 反代 llama-server(127.0.0.1:8081)
#  思路: 以「最近一次推理请求」判定活跃，而不是看 GPU 利用率。
#         - 主信号: nginx access_log(/var/log/nginx/access.log) 的修改时间
#                   (nginx 在每次请求结束时写一行 access log => 准确的“请求完成”事件,
#                    天然忽略 keep-alive 长连接，不会误判成活跃)
#         - 辅信号: llama-server 的活动日志 mtime
#         - 在途兜底: llama-server /metrics 里当前正在处理的请求数(>0 视为活跃)
#         - 手动防误杀: 存在 /tmp/.llm-keep-awake 则不关机
#  当“最近一次服务活动”距今 >= IDLE_SECS(默认 3600s=1h) 且无在途请求时关机。
# =============================================================================
set -uo pipefail

# ---------------- 配置(可通过环境变量覆盖) ----------------
IDLE_SECS="${IDLE_SECS:-3600}"                 # 空闲阈值(秒)，3600 = 1 小时
DRYRUN="${DRYRUN:-0}"                          # 1 = 只记录不真正关机(测试用)
KEEP_AWAKE_FILE="${KEEP_AWAKE_FILE:-/tmp/.llm-keep-awake}"   # 存在则本次跳过
STATE_FILE="${STATE_FILE:-/var/tmp/llm_last_serving}"        # 无任何服务日志时的基线时间戳
LOG="${LOG:-/root/autodl-tmp/idle_shutdown.log}"
METRICS_URL="${METRICS_URL:-http://127.0.0.1:8081/metrics}"  # llama-server prometheus
# 参与“最近活动”判定的日志文件(越靠前越优先)
SERVING_LOGS=(
  "/var/log/nginx/access.log"
  "/root/autodl-tmp/server_coletti.log"
)
# ----------------

now()   { date +%s; }
nowiso(){ date '+%F %T'; }
log()   { echo "[$(nowiso)] $*" >> "$LOG"; }
max(){ if [ "$1" -ge "$2" ]; then echo "$1"; else echo "$2"; fi }

NOW=$(now)
LATEST=0

# 1) 最近一次“服务活动”(请求完成/服务器写入日志)时间
for f in "${SERVING_LOGS[@]}"; do
  if [ -f "$f" ]; then
    ts=$(stat -c %Y "$f" 2>/dev/null || echo 0)
    [ "${ts:-0}" -gt 0 ] && LATEST=$(max "$LATEST" "$ts")
  fi
done

# 2) 基线: 若两台日志都不存在/无记录(刚安装、无卡模式 server 没跑)，
#    用安装(或上次启动)标记做基线，避免一装上就立刻误关机。
if [ ! -f "$STATE_FILE" ]; then
  echo "$NOW" > "$STATE_FILE" 2>/dev/null || true
fi
BOOT_TS=$(stat -c %Y "$STATE_FILE" 2>/dev/null || echo 0)
[ "${BOOT_TS:-0}" -gt 0 ] && LATEST=$(max "$LATEST" "$BOOT_TS")

IDLE=$(( NOW - LATEST ))

# 3) 手动免关机(管理员在干活时不想被关)
if [ -f "$KEEP_AWAKE_FILE" ]; then
  log "keep-awake 存在, 跳过 (idle=${IDLE}s)"
  exit 0
fi

# 4) 在途请求兜底: 即使“超时”, 只要 llama-server 当前还在处理请求就不关机
if [ "$IDLE" -ge "$IDLE_SECS" ]; then
  if command -v curl >/dev/null 2>&1; then
    PROC=$(curl -s --max-time 5 "$METRICS_URL" 2>/dev/null \
      | grep -iE 'request.*(process|act|run)|(process|act|run).*request' \
      | awk '$2>0{print $2}' | sort -rn | head -1 || true)
    if [ -n "${PROC:-}" ] && [ "${PROC:-0}" -gt 0 ]; then
      log "检测到在途请求(metrics), 视为活跃, 不关机 (idle=${IDLE}s)"
      exit 0
    fi
  fi
fi

# 5) 还有服务活动 -> 不关机
if [ "$IDLE" -lt "$IDLE_SECS" ]; then
  log "活跃(距最近服务活动 ${IDLE}s < ${IDLE_SECS}s), 不关机"
  exit 0
fi

# 6) 已连续空闲超过阈值 -> 关机
log "=== 空闲已达 ${IDLE}s >= ${IDLE_SECS}s, 触发关机 ==="
log "LATEST_ACTIVITY_TS=${LATEST}"
if [ "$DRYRUN" -eq 1 ]; then
  log "[DRYRUN] 本应执行: shutdown -h now"
  echo "DRYRUN: 即将关机 (见 $LOG)"
  exit 0
fi
log "执行: shutdown -h now"
shutdown -h now 2>>"$LOG" || poweroff -f 2>>"$LOG"
exit 0
