#!/usr/bin/env bash
echo "=== GPU ==="; nvidia-smi 2>&1 | head -16
echo "=== cgroup mem ==="; cat /sys/fs/cgroup/memory.max 2>/dev/null
echo "=== cpu ==="; nproc; free -h | head -2
echo "=== disk ==="; df -h / 2>/dev/null | tail -1; df -h /root/autodl-tmp 2>/dev/null | tail -1
echo "=== cuda ==="; ls /usr/local/ | grep -i cuda; /usr/local/cuda/bin/nvcc -V 2>/dev/null | tail -1
echo "=== network_turbo ==="; ls -la /etc/network_turbo 2>&1; head -3 /etc/network_turbo 2>&1
echo "=== build tools ==="; for t in git cmake gcc g++ make aria2c python3; do printf "%-10s %s\n" "$t" "$(command -v $t || echo NONE)"; done
echo "=== /root/autodl-tmp ==="; ls -la /root/autodl-tmp 2>&1 | head
echo "=== test turbo to github/hf ==="; source /etc/network_turbo >/dev/null 2>&1; curl -s -o NUL -w 'hf http=%{http_code} time=%{time_total}s\n' --max-time 15 https://huggingface.co 2>&1; curl -s -o NUL -w 'gfw=%{http_code}\n' --max-time 15 https://github.com 2>&1
