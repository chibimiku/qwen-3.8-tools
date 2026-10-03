#!/usr/bin/env bash
set -uo pipefail
source /etc/network_turbo >/dev/null 2>&1 || true
export DEBIAN_FRONTEND=noninteractive
echo "=== install nginx ==="
apt-get update -qq 2>&1 | tail -1
apt-get install -y -qq nginx 2>&1 | tail -2
echo "=== place config ==="
cp /root/autodl-tmp/nginx_coletti.conf /etc/nginx/sites-available/coletti.conf
ln -sf /etc/nginx/sites-available/coletti.conf /etc/nginx/sites-enabled/coletti.conf
nginx -t 2>&1 | tail -2
echo "=== start nginx ==="
(nginx 2>&1 | tail -2) || pgrep nginx >/dev/null && echo "nginx running"
echo "=== monitor wrapper ==="
cat > /root/autodl-tmp/run_monitor_coletti.sh <<'EOF'
#!/usr/bin/env bash
exec /root/miniconda3/bin/python3 /root/autodl-tmp/monitor_coletti.py
EOF
chmod +x /root/autodl-tmp/run_monitor_coletti.sh
pkill -9 -f monitor_coletti 2>/dev/null; sleep 1
nohup /root/autodl-tmp/run_monitor_coletti.sh > /root/autodl-tmp/monitor_coletti.log 2>&1 &
echo "monitor pid=$!"
sleep 3
echo "=== verify ==="
curl -s --max-time 6 http://127.0.0.1:8080/v1/models -o /dev/null -w '8080/v1/models -> %{http_code}\n'
curl -s --max-time 6 http://127.0.0.1:8080/health -o /dev/null -w '8080/health -> %{http_code}\n'
curl -s --max-time 6 http://127.0.0.1:8080/monitor/ -o /dev/null -w '8080/monitor -> %{http_code}\n'
echo "NGINX_MONITOR_DONE"
