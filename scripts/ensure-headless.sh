#!/bin/bash
# 确保 headless Chromium 在 CDP 端口 9222 上运行
# 可被心跳或其他脚本调用

CDP_PORT=9222

if curl -s --max-time 3 "http://127.0.0.1:${CDP_PORT}/json/version" > /dev/null 2>&1; then
    echo "✅ headless Chromium running on port ${CDP_PORT}"
    exit 0
fi

echo "⚠️  headless Chromium not running, starting..."
nohup chromium \
    --headless=new --no-sandbox --disable-gpu --disable-dev-shm-usage \
    --disable-extensions --disable-background-networking --disable-default-apps \
    --remote-debugging-port="${CDP_PORT}" --remote-debugging-address=127.0.0.1 \
    --remote-allow-origins=* \
    --user-data-dir=/tmp/opencli-headless-profile \
    about:blank > /tmp/opencli-headless.log 2>&1 &

sleep 6

if curl -s --max-time 5 "http://127.0.0.1:${CDP_PORT}/json/version" > /dev/null 2>&1; then
    echo "✅ headless Chromium started successfully"
else
    echo "❌ Failed to start headless Chromium"
    cat /tmp/opencli-headless.log 2>/dev/null | tail -10
    exit 1
fi
