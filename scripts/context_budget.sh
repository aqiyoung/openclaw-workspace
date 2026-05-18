#!/bin/bash

# Context Budget Monitor
# 监控上下文使用情况，超过阈值时告警
# 参考 Claude Code 的 autoCompact 设计

set -e

# 配置阈值
WARN_THRESHOLD=70    # 警告
ALERT_THRESHOLD=80   # 提醒
CRITICAL_THRESHOLD=90 # 紧急

# 状态文件
STATE_FILE="/tmp/openclaw/context_budget.json"
HISTORY_FILE="$HOME/.openclaw/context_history.jsonl"

# 获取当前上下文信息（从 session_status 解析）
# 这里假设已经通过其他方式获取了 context 使用率
# 实际使用时由 agent 在心跳时传入

# 读取状态
read_state() {
    if [[ -f "$STATE_FILE" ]]; then
        cat "$STATE_FILE"
    else
        echo '{"used_pct": 0, "last_check": null}'
    fi
}

# 写入状态
write_state() {
    local used_pct=$1
    local status=$2
    local timestamp=$(date -Iseconds)
    
    cat > "$STATE_FILE" <<EOF
{
    "used_pct": $used_pct,
    "status": "$status",
    "last_check": "$timestamp",
    "thresholds": {
        "warn": $WARN_THRESHOLD,
        "alert": $ALERT_THRESHOLD,
        "critical": $CRITICAL_THRESHOLD
    }
}
EOF
}

# 记录历史
log_history() {
    local used_pct=$1
    local status=$2
    local timestamp=$(date -Iseconds)
    
    echo "{\"ts\": \"$timestamp\", \"used_pct\": $used_pct, \"status\": \"$status\"}" >> "$HISTORY_FILE"
    
    # 只保留最近 1000 条
    tail -n 1000 "$HISTORY_FILE" > "${HISTORY_FILE}.tmp"
    mv "${HISTORY_FILE}.tmp" "$HISTORY_FILE"
}

# 判断状态等级
get_status() {
    local used_pct=$1
    
    if awk -v pct="$used_pct" -v thresh="$CRITICAL_THRESHOLD" 'BEGIN{exit!(pct>=thresh)}'; then
        echo "critical"
    elif awk -v pct="$used_pct" -v thresh="$ALERT_THRESHOLD" 'BEGIN{exit!(pct>=thresh)}'; then
        echo "alert"
    elif awk -v pct="$used_pct" -v thresh="$WARN_THRESHOLD" 'BEGIN{exit!(pct>=thresh)}'; then
        echo "warn"
    else
        echo "ok"
    fi
}

# 发送告警（通过 openclaw message）
send_alert() {
    local used_pct=$1
    local status=$2
    local message=""
    
    case $status in
        critical)
            message="🔴 上下文紧急：已使用 ${used_pct}%，请立即清理或重启会话"
            ;;
        alert)
            message="🟠 上下文告警：已使用 ${used_pct}%，建议清理旧记忆"
            ;;
        warn)
            message="🟡 上下文警告：已使用 ${used_pct}%，注意监控"
            ;;
    esac
    
    # 只有 alert 和 critical 才推送到微信
    if [[ "$status" == "alert" || "$status" == "critical" ]]; then
        openclaw message send --channel openclaw-weixin --message "$message" 2>/dev/null || true
    fi
}

# 主函数
# 参数：$1 = used_pct (0-100)
main() {
    local used_pct=${1:-0}
    
    # 验证输入
    if ! [[ "$used_pct" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        echo "Error: used_pct must be a number" >&2
        exit 1
    fi
    
    # 获取状态
    local status=$(get_status $used_pct)
    
    # 写入状态
    write_state "$used_pct" "$status"
    
    # 记录历史
    log_history "$used_pct" "$status"
    
    # 如果状态异常，发送告警
    if [[ "$status" != "ok" ]]; then
        send_alert "$used_pct" "$status"
    fi
    
    # 输出状态（供 agent 读取）
    echo "Context budget: ${used_pct}% (${status})"
}

# 如果带参数运行
if [[ $# -gt 0 ]]; then
    main "$1"
fi
