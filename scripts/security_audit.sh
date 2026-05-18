#!/bin/bash
# 安全审计脚本 - 每天 8:00 运行
# 推送结果到 Telegram

set -e

# 确保 PATH 包含 Docker
export PATH="/usr/bin:/home/liyang/.nvm/versions/node/v24.15.0/bin:/home/liyang/.opencode/bin:/home/liyang/.local/nodejs/bin:/home/liyang/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/home/liyang/.local/bin:/home/liyang/bin"

# 强制中文输出
export LANG=C.utf8
export LC_ALL=C.utf8

# 输出结果（由 cron delivery 统一发送到 Telegram）
send_telegram() {
    local message="$1"
    echo "$message"
}

# 主审计逻辑
audit_result="🔒 安全审计 $(date '+%Y-%m-%d %H:%M:%S')"

# 1. 系统更新检查
audit_result="${audit_result}

📦 系统更新:"
if command -v apt &> /dev/null; then
    updates=$(apt list --upgradable 2>/dev/null | wc -l)
    if [ "$updates" -gt 0 ]; then
        audit_result="${audit_result}
⚠️ 有 ${updates} 个包可更新"
    else
        audit_result="${audit_result}
✅ 系统已是最新"
    fi
else
    audit_result="${audit_result}
❓ 未检测到 apt 包管理器"
fi

# 2. 磁盘使用检查
audit_result="${audit_result}

💾 磁盘使用:"
while IFS= read -r line; do
    usage=$(echo "$line" | awk '{print $5}' | sed 's/%//')
    mount=$(echo "$line" | awk '{print $6}')
    if [ "$usage" -gt 80 ]; then
        audit_result="${audit_result}
⚠️ ${mount}: ${usage}%"
    else
        audit_result="${audit_result}
✅ ${mount}: ${usage}%"
    fi
done < <(df -h | grep -E '^/dev/' | grep -v '/vol00/')

# 3. 内存使用检查
audit_result="${audit_result}

🧠 内存使用:"
mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [ "$mem_usage" -gt 80 ]; then
    audit_result="${audit_result}
⚠️ 内存使用: ${mem_usage}%"
else
    audit_result="${audit_result}
✅ 内存使用: ${mem_usage}%"
fi

# 4. 开放端口检查
audit_result="${audit_result}

🌐 开放端口:"
listening_ports=$(ss -tuln | grep LISTEN | wc -l)
audit_result="${audit_result}
📊 监听端口数: ${listening_ports}"

# 5. 失败登录检查（最近 24 小时）
audit_result="${audit_result}

🔐 失败登录:"
if [ -r /var/log/auth.log ]; then
    failed_logins=$(grep "Failed password" /var/log/auth.log | grep "$(date '+%b %d')" | wc -l)
    if [ "$failed_logins" -gt 10 ]; then
        audit_result="${audit_result}
⚠️ 今日失败登录: ${failed_logins} 次"
    else
        audit_result="${audit_result}
✅ 今日失败登录: ${failed_logins} 次"
    fi
else
    audit_result="${audit_result}
❓ 无权限读取 auth.log"
fi

# 6. Docker 容器状态
audit_result="${audit_result}

🐳 Docker 容器:"
if command -v docker &> /dev/null; then
    running_containers=$(docker ps --format '{{.Names}}' | wc -l)
    stopped_containers=$(docker ps -a --filter "status=exited" --format '{{.Names}}' | wc -l)
    audit_result="${audit_result}
✅ 运行中: ${running_containers}
⏹️ 已停止: ${stopped_containers}"
else
    audit_result="${audit_result}
❓ Docker 未安装"
fi

# 7. OpenClaw Gateway 状态
audit_result="${audit_result}

🤖 OpenClaw Gateway:"
if pgrep -f "openclaw.*gateway" > /dev/null; then
    audit_result="${audit_result}
✅ Gateway 运行中"
else
    audit_result="${audit_result}
❌ Gateway 未运行"
fi

# 8. systemd timers 状态
audit_result="${audit_result}

⏰ 定时任务:"
timers_status=$(systemctl --user list-timers --all 2>&1 | grep -E "smart-home-monitor|nas-monitor|openclaw-restart-notify" | wc -l)
if [ "$timers_status" -ge 3 ]; then
    audit_result="${audit_result}
✅ 3 个定时器正常"
else
    audit_result="${audit_result}
⚠️ 定时器异常: ${timers_status} 个"
fi

# 发送结果
send_telegram "${audit_result}"

echo "安全审计完成"
