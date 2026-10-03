#!/usr/bin/env bash
set -euo pipefail
source /etc/network_turbo >/dev/null 2>&1 || true
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
BIN=/root/autodl-tmp/llama.cpp/build/bin/llama-server
MODEL=/root/autodl-tmp/models/Qwen3.8-27B-Uncensored-Q8_0.gguf
exec "$BIN" \
  --model "$MODEL" \
  --alias "qwen-novel,$MODEL" \
  --spec-type draft-mtp \
  --spec-draft-n-max 2 \
  --spec-draft-p-min 0 \
  --ctx-size 131072 \
  --parallel 1 \
  --batch-size 2048 \
  --ubatch-size 512 \
  --n-gpu-layers all \
  --split-mode none \
  --flash-attn on \
  --load-mode none \
  --jinja \
  --reasoning off \
  --repeat-penalty 1.0 \
  --presence-penalty 1.5 \
  --temp 0.7 \
  --top-p 0.8 \
  --top-k 20 \
  --min-p 0 \
  --metrics \
  --host 0.0.0.0 \
  --port 8081
