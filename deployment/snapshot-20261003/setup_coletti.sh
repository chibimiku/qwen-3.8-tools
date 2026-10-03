#!/usr/bin/env bash
set -uo pipefail
source /etc/network_turbo >/dev/null 2>&1 || echo "WARN turbo"
export PATH=/usr/local/cuda-12.1/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
BASEDIR=/root/autodl-tmp
SRC=$BASEDIR/llama.cpp
echo "setup start $(date)"
echo "=== install aria2c ==="
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq 2>&1 | tail -2
apt-get install -y -qq aria2 2>&1 | tail -2
command -v aria2c && echo "aria2 ok"
echo "=== clone llama.cpp (latest main, has MTP) ==="
cd "$BASEDIR"
rm -rf "$SRC"
git clone --depth 1 https://github.com/ggml-org/llama.cpp "$SRC" 2>&1 | tail -3
echo "clone done; entries=$(ls $SRC | wc -l)"
echo "SETUP_OK"
