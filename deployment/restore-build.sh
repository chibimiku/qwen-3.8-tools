#!/usr/bin/env bash
# Rebuild from the source archive captured from the working instance.
# Run on the NEW Linux server after uploading this repository.
set -euo pipefail
SNAPSHOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/snapshot-20261003" && pwd)"
LLM_ROOT="${LLM_ROOT:-/root/autodl-tmp}"
GPU_ARCH="${GPU_ARCH:-89}"
BUILD_JOBS="${BUILD_JOBS:-8}"
CUDA_ROOT="${CUDA_ROOT:-/usr/local/cuda-12.1}"
if [[ -x "$CUDA_ROOT/bin/nvcc" ]]; then
  export PATH="$CUDA_ROOT/bin:$PATH"
  export LD_LIBRARY_PATH="$CUDA_ROOT/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
command -v cmake >/dev/null
command -v nvcc >/dev/null
command -v g++ >/dev/null
mkdir -p "$LLM_ROOT"
if [[ -e "$LLM_ROOT/llama.cpp" ]]; then
  echo "Refusing to overwrite existing $LLM_ROOT/llama.cpp; choose a fresh LLM_ROOT." >&2
  exit 1
fi
mkdir "$LLM_ROOT/llama.cpp"
tar -xzf "$SNAPSHOT_DIR/llama-source-audit.tar.gz" -C "$LLM_ROOT/llama.cpp"
cmake -S "$LLM_ROOT/llama.cpp" -B "$LLM_ROOT/llama.cpp/build" \
  -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release \
  -DGGML_CUDA_ARCHITECTURES="$GPU_ARCH" -DCMAKE_CUDA_ARCHITECTURES="$GPU_ARCH" \
  -DLLAMA_BUILD_MTMD=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_LLGUIDANCE=OFF
cmake --build "$LLM_ROOT/llama.cpp/build" --config Release --parallel "$BUILD_JOBS"
echo "Built captured llama.cpp source. Original commit is recorded in snapshot manifest.json."
echo "Download and verify the model separately, then install the saved launch scripts."
