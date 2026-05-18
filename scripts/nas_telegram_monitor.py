#!/usr/bin/env python3
"""飞牛NAS事件推送 - 简化版"""

import sqlite3, time, json, os, re, subprocess
from datetime import datetime, timezone, timedelta

# 加载环境变量
_env = os.path.expanduser("~/.openclaw/gateway.systemd.env")
if os.path.exists(_env):
    with open(_env) as f:
        for l in f:
            l = l.strip()
            if l and not l.startswith('#') and '=' in l:
                k, v = l.split('=', 1)
                os.environ[k.strip()] = v.strip()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT = "460212872"
DB = "/usr/trim/var/eventlogger_service/logger_data.db3"
NGINX = "/usr/trim/nginx/logs/access.log"
CURSOR = "/vol1/1000/FNMessageBots/data/cursor"
os.makedirs(CURSOR, exist_ok=True)

def send(text):
    import requests
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": CHAT, "text": text, "parse_mode": "HTML"},
            proxies={"https": "http://127.0.0.1:7890"}, timeout=10
        )
        return r.json().get("ok", False)
    except:
        return False

def check_db():
    f = os.path.join(CURSOR, "db_cursor.txt")
    last = int(open(f).read()) if os.path.exists(f) else 0
    try:
        c = sqlite3.connect(DB, timeout=5)
        rows = c.execute("SELECT id,eventId,uname,logtime FROM log WHERE id>? ORDER BY id LIMIT 50", (last,)).fetchall()
        c.close()
        for eid, etype, uname, ts in rows:
            dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=8)))
            name = {"LoginSucc":"✅ 登录成功","LoginFail":"❌ 登录失败"}.get(etype, f"📌 {etype}")
            msg = f"<b>飞牛NAS · {name}</b>\n⏰ {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            if uname: msg += f"\n👤 {uname}"
            send(msg)
            last = eid
            time.sleep(0.3)
        if last:
            with open(f, "w") as fp: fp.write(str(last))
    except Exception as e:
        print(f"DB err: {e}")

def check_nginx():
    f = os.path.join(CURSOR, "nginx_offset.txt")
    off = int(open(f).read()) if os.path.exists(f) else 0
    try:
        if not os.path.exists(NGINX): return
        sz = os.path.getsize(NGINX)
        if sz <= off: return
        with open(NGINX) as fp:
            fp.seek(off)
            lines = fp.readlines()
        with open(f, "w") as fp: fp.write(str(sz))
        for l in lines:
            if "accountapi" in l and "websocket" not in l:
                ip = l.split()[0]
                send(f"<b>飞牛NAS · 📱 App登录</b>\n🌐 IP: {ip}\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"nginx err: {e}")

def check_ssh():
    try:
        r = subprocess.run(
            ["journalctl","-u","sshd","--since","6 min ago","-q","--no-pager","-o","json"],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode != 0 or not r.stdout.strip(): return
        for line in r.stdout.strip().split("\n"):
            if not line.strip(): continue
            try:
                e = json.loads(line)
                msg = e.get("MESSAGE","")
                ts = e.get("__REALTIME_TIMESTAMP","")
                if "Accepted" not in msg: continue
                m = re.search(r'Accepted \w+ for (\S+) from (\S+) port \d+', msg)
                if not m: continue
                user, ip = m.group(1), m.group(2)
                t = "unknown"
                if ts:
                    dt = datetime.fromtimestamp(int(ts)/1e6, tz=timezone(timedelta(hours=8)))
                    t = dt.strftime("%Y-%m-%d %H:%M:%S")
                send(f"<b>飞牛NAS · ✅ SSH 登录成功</b>\n⏰ {t}\n👤 {user}\n🌐 {ip}")
                print(f"SSH: {user}@{ip}")
                time.sleep(0.5)
            except: pass
    except Exception as e:
        print(f"SSH err: {e}")

print("🚀 飞牛NAS监控启动")
send("🚀 飞牛NAS监控启动")

while True:
    try:
        check_db()
        check_nginx()
        check_ssh()
    except Exception as e:
        print(f"err: {e}")
    time.sleep(5)
