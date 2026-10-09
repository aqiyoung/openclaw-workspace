#!/bin/bash
export PATH="/home/liyang/.nvm/versions/node/v26.5.0/bin:$PATH"
LOG_DIR="/home/liyang/.openclaw/workspace/logs/audit"
mkdir -p "$LOG_DIR"
DATE=$(date +%Y%m%d-%H%M%S)

# 1. OpenClaw security audit
echo "=== OpenClaw Security Audit ===" > "$LOG_DIR/openclaw-audit-$DATE.log"
cd /home/liyang/.openclaw/workspace && openclaw security audit --deep >> "$LOG_DIR/openclaw-audit-$DATE.log" 2>&1

# 2. Lynis system audit
echo "=== Lynis System Audit ===" > "$LOG_DIR/lynis-audit-$DATE.log"
sudo lynis audit system --quick >> "$LOG_DIR/lynis-audit-$DATE.log" 2>&1

# 3. Summary
OPENCLAW_ISSUES=$(grep -ci "issue\|warning\|critical\|error\|risk" "$LOG_DIR/openclaw-audit-$DATE.log" 2>/dev/null || echo 0)
LYNIS_WARNINGS=$(grep -ci "Warning\|suggestion\|vulnerability" "$LOG_DIR/lynis-audit-$DATE.log" 2>/dev/null || echo 0)

# 4. Notify via Telegram
TOKEN="$(source /home/liyang/.openclaw/.env 2>/dev/null && echo "$TELEGRAM_BOT_TOKEN")"
CHAT_ID="460212872"
MSG="🔐 每日安全审计完成
├─ OpenClaw: $OPENCLAW_ISSUES 个问题
├─ Lynis: $LYNIS_WARNINGS 个警告
└─ 详情: logs/audit/openclaw-audit-$DATE.log"

curl -s -X POST "https://api.telegram.org/bot$TOKEN/sendMessage" \
  -d "chat_id=$CHAT_ID" \
  -d "text=$MSG" \
  -d "parse_mode=Markdown" > /dev/null 2>&1

# 5. Push to OpenClaw app via agent message
openclaw agent -m "🔐 每日安全审计完成 — OpenClaw: $OPENCLAW_ISSUES 个问题, Lynis: $LYNIS_WARNINGS 个警告" --deliver > /dev/null 2>&1

# Keep only last 30 days of logs
find "$LOG_DIR" -name "*.log" -mtime +30 -delete 2>/dev/null