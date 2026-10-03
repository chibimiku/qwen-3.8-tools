#!/usr/bin/env bash
set -uo pipefail
source /etc/network_turbo >/dev/null 2>&1 || true
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
SRC=/root/autodl-tmp/llama.cpp
echo "build start $(date)"
cd "$SRC"
echo "=== cmake configure ==="
cmake -S . -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA_ARCHITECTURES=89 -DCMAKE_CUDA_ARCHITECTURES=89 2>&1 | tail -6
echo "=== build -j32 ==="
cmake --build build --config Release -j 32 2>&1 | tail -12
echo "BUILD_DONE $(date)"
ls -lh build/bin/llama-server 2>/dev/null
