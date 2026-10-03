#!/usr/bin/env bash
set -uo pipefail
source /etc/network_turbo >/dev/null 2>&1 || echo "WARN turbo"
MODELS=/root/autodl-tmp/models
BASE="https://huggingface.co/JonathanColetti/Qwen3.8-27B-Uncensored-GGUF/resolve/main"
mkdir -p "$MODELS"
echo "dl start $(date)"
dl() {
  local f="$1"
  echo "=== aria2 -x16 $f ==="
  aria2c -x 16 -s 16 -k 1M -c --file-allocation=none \
    --max-connection-per-server=16 --min-split-size=1M \
    --console-log-level=warn --summary-interval=20 \
    -d "$MODELS" -o "$f" "$BASE/$f" 2>&1 | tail -4
  ls -lh "$MODELS/$f" 2>/dev/null
}
dl "Qwen3.8-27B-Uncensored-Q8_0.gguf"
dl "mmproj-Qwen3.8-27B-Uncensored-F16.gguf"
echo "MODELS_DONE $(date)"; du -sh "$MODELS"
