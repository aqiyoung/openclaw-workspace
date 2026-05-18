#!/bin/bash
# mihomo-speedtest.sh — 每30分钟测速并推送最优节点到 Telegram
python3 << 'PYEOF'
import json, yaml, urllib.request, subprocess, sys, socket, os, time
from datetime import datetime

for k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'all_proxy', 'ALL_PROXY']:
    os.environ.pop(k, None)

BOT_TOKEN = "8089763706:AAFOMFwECiCXIrPc7R9H47BL91pru3ErnIg"
CHAT_ID = "460212872"

with open('/home/liyang/.config/mihomo/config.yaml') as f:
    config = yaml.safe_load(f)
config_proxies = {p.get('name', ''): p for p in config.get('proxies', [])}

# 获取当前自动选择的最优节点
auto_raw = subprocess.run(
    ['curl', '-s', 'http://127.0.0.1:9090/proxies/%E2%99%BB%EF%B8%8F%20%E8%87%AA%E5%8A%A8%E9%80%89%E6%8B%A9'],
    capture_output=True, text=True, timeout=10
).stdout
auto_data = json.loads(auto_raw)
best_name = auto_data.get('now', '')

if not best_name:
    print("无法获取自动选择节点"); sys.exit(1)

# 获取延迟历史
api_raw = subprocess.run(['curl', '-s', 'http://127.0.0.1:9090/proxies'], capture_output=True, text=True, timeout=10).stdout
api_data = json.loads(api_raw)
best_info = api_data.get("proxies", {}).get(best_name, {})
history = best_info.get("history", [])
delays = [h.get("delay", 0) for h in history[-3:] if h.get("delay", 0) > 0]
best_delay = int(sum(delays) / len(delays)) if delays else 0

# 获取服务器信息
cfg = config_proxies.get(best_name, {})
server = cfg.get("server", "")
port = cfg.get("port", 443)

# TCP 直连测速（3次取平均）
node_ip = server
try:
    node_ip = socket.gethostbyname(server)
except:
    pass

tcp_delays = []
for _ in range(3):
    try:
        start = datetime.now()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((node_ip, port))
        sock.close()
        end = datetime.now()
        d = int((end - start).total_seconds() * 1000)
        tcp_delays.append(d)
    except:
        pass
    time.sleep(0.5)
tcp_avg = int(sum(tcp_delays) / len(tcp_delays)) if tcp_delays else 0

# 查节点 IP 信息
node_country = node_city = node_isp = ""
try:
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    resp = opener.open(f'http://ip-api.com/json/{node_ip}?fields=query,country,city,isp', timeout=8)
    d = json.loads(resp.read())
    node_country = d.get("country", "")
    node_city = d.get("city", "")
    node_isp = d.get("isp", "")
except:
    pass

# 查本地 IP
local_ip = local_country = local_city = local_isp = ""
try:
    proxy_handler = urllib.request.ProxyHandler({})
    opener = urllib.request.build_opener(proxy_handler)
    resp = opener.open('http://ip-api.com/json/?fields=query,country,city,isp', timeout=8)
    d = json.loads(resp.read())
    local_ip = d.get("query", "")
    local_country = d.get("country", "")
    local_city = d.get("city", "")
    local_isp = d.get("isp", "")
except:
    pass

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

lines = []
lines.append("🎯 当前最优代理")
lines.append("")
lines.append(f"✅ 节点: {best_name}")
lines.append(f"⏱ mihomo延迟: {best_delay}ms")
if tcp_avg > 0:
    lines.append(f"⏱ TCP实测: {tcp_avg}ms")
lines.append(f"🖥 服务器: {server}:{port}")
lines.append(f"🌍 节点IP: {node_ip}")
if node_country:
    loc = node_country
    if node_city:
        loc += f", {node_city}"
    lines.append(f"🌍 节点地区: {loc}")
    if node_isp:
        lines.append(f"🏢 节点ISP: {node_isp}")
if local_ip:
    lines.append(f"🏠 本地IP: {local_ip}")
if local_country:
    loc = local_country
    if local_city:
        loc += f", {local_city}"
    lines.append(f"🏠 本地地区: {loc}")
    if local_isp:
        lines.append(f"🏢 本地ISP: {local_isp}")
lines.append("")
lines.append(f"📊 总节点: {len(config_proxies)} 个")
lines.append(f"📌 订阅: threely.pages.dev")
lines.append("")
lines.append("🤖 自动优选 | 每30分钟")

msg = "\n".join(lines)

payload = json.dumps({"chat_id": CHAT_ID, "text": msg}).encode("utf-8")
req = urllib.request.Request(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"}
)
try:
    proxy_handler = urllib.request.ProxyHandler({"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"})
    opener = urllib.request.build_opener(proxy_handler)
    resp = opener.open(req, timeout=15)
    print(f"[{now}] 已推送: {best_name} ({best_delay}ms, TCP {tcp_avg}ms)")
except Exception as e:
    print(f"[{now}] 推送失败: {e}")
PYEOF
