#!/bin/bash
# opencli-headless 启动脚本 — 带自动重启
CDP_PORT=9222
PROFILE_DIR="/tmp/opencli-headless-profile"
LOG="/tmp/opencli-headless.log"

# 清理旧进程
pkill -f "chromium.*${CDP_PORT}" 2>/dev/null
sleep 1

while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting headless Chromium on port ${CDP_PORT}..." >> "$LOG"
    chromium \
        --headless=new \
        --no-sandbox \
        --disable-gpu \
        --disable-dev-shm-usage \
        --disable-extensions \
        --disable-background-networking \
        --disable-default-apps \
        --remote-debugging-port="${CDP_PORT}" \
        --remote-debugging-address=127.0.0.1 \
        --user-data-dir="${PROFILE_DIR}" \
        about:blank >> "$LOG" 2>&1 &
    
    PID=$!
    sleep 5
    
    # 检查是否启动成功
    if curl -s --max-time 3 "http://127.0.0.1:${CDP_PORT}/json/version" > /dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Chromium ready (PID $PID)" >> "$LOG"
        wait $PID
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Chromium exited, restarting..." >> "$LOG"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Chromium failed to start, retrying..." >> "$LOG"
        kill $PID 2>/dev/null
        sleep 3
    fi
done
