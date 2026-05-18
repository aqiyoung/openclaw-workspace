#!/bin/bash

# Memory Cleanup (MicroCompact)
# 选择性清理过期记忆，保留骨架，丢弃过程数据
# 参考 Claude Code 的 microCompact 模式

set -e

MEMORY_DIR="$HOME/.openclaw/workspace/memory"
COST_DIR="$HOME/.openclaw/cost_tracker"
HEARTBEAT_LOG="$HOME/.openclaw/workspace/memory/heartbeat-state.json"
CLEANUP_LOG="/tmp/openclaw/cleanup.log"

# 配置保留天数
WEATHER_KEEP_DAYS=7       # 天气数据保留 7 天
COST_KEEP_DAYS=30         # 费用记录保留 30 天
LOG_KEEP_DAYS=14          # 日志保留 14 天
TASK_KEEP_DAYS=3          # 已完成任务详情保留 3 天

log() {
    echo "[$(date -Iseconds)] $*" >> "$CLEANUP_LOG"
}

# 清理旧的记忆文件（按日期命名的）
cleanup_daily_memories() {
    local count=0
    local today=$(date +%Y-%m-%d)
    local cutoff=$(date -d "-30 days" +%Y-%m-%d 2>/dev/null || date -v-30d +%Y-%m-%d 2>/dev/null)
    
    if [[ ! -d "$MEMORY_DIR" ]]; then
        return
    fi
    
    for f in "$MEMORY_DIR"/*.md; do
        [[ -f "$f" ]] || continue
        local basename=$(basename "$f")
        local file_date=$(echo "$basename" | grep -oP '^\d{4}-\d{2}-\d{2}' || true)
        
        # 只清理日期命名的文件，跳过 MEMORY.md 等
        [[ -z "$file_date" ]] && continue
        [[ "$basename" == "MEMORY.md" ]] && continue
        
        # 判断是否过期
        if [[ "$file_date" < "$cutoff" ]]; then
            # 压缩而非删除：提取关键信息，丢弃过程数据
            local backup="${f}.archived"
            log "Archiving old memory: $basename"
            
            # 提取包含关键词的行（决策、偏好、重要事项）
            grep -iE '(偏好|决策|规则|铁律|重要|必须|永远|never|always|important|decision)' "$f" > "$backup" 2>/dev/null || true
            
            # 如果提取后为空，说明没有关键信息，直接清理
            if [[ ! -s "$backup" ]]; then
                rm "$backup"
                log "No critical info in $basename, removed"
            else
                log "Kept critical lines from $basename"
            fi
            
            ((count++))
        fi
    done
    
    log "Daily memory cleanup: processed $count files"
}

# 清理费用追踪记录
cleanup_cost_tracker() {
    if [[ ! -d "$COST_DIR" ]]; then
        return
    fi
    
    local cutoff=$(date -d "-${COST_KEEP_DAYS} days" +%s 2>/dev/null || date -v-${COST_KEEP_DAYS}d +%s 2>/dev/null)
    local count=0
    
    for f in "$COST_DIR"/*.jsonl; do
        [[ -f "$f" ]] || continue
        local basename=$(basename "$f" .jsonl)
        local file_date=$(echo "$basename" | grep -oP '^\d{4}-\d{2}-\d{2}' || true)
        
        [[ -z "$file_date" ]] && continue
        
        local file_ts=$(date -d "$file_date" +%s 2>/dev/null || date -jf "%Y-%m-%d" "$file_date" +%s 2>/dev/null || echo 0)
        
        if [[ "$file_ts" -lt "$cutoff" ]]; then
            log "Removing old cost file: $basename"
            rm "$f"
            ((count++))
        fi
    done
    
    log "Cost tracker cleanup: removed $count files"
}

# 清理 heartbeat 状态中的旧数据
cleanup_heartbeat_state() {
    if [[ ! -f "$HEARTBEAT_LOG" ]]; then
        return
    fi
    
    # 保留最近 24 小时的检查记录
    local cutoff=$(date -d "-24 hours" +%s 2>/dev/null || date -v-24H +%s 2>/dev/null)
    local temp_file="${HEARTBEAT_LOG}.tmp"
    
    python3 -c "
import json, sys
try:
    with open('$HEARTBEAT_LOG') as f:
        data = json.load(f)
    
    cutoff = $cutoff
    if 'lastChecks' in data:
        for key in list(data['lastChecks'].keys()):
            ts = data['lastChecks'][key]
            if isinstance(ts, (int, float)) and ts < cutoff * 1000:
                del data['lastChecks'][key]
    
    with open('$temp_file', 'w') as f:
        json.dump(data, f, indent=2)
    print('cleaned')
except Exception as e:
    print(f'error: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null && mv "$temp_file" "$HEARTBEAT_LOG" || true
    
    log "Heartbeat state cleanup done"
}

# 清理临时文件
cleanup_temp_files() {
    local count=0
    
    # 清理超过 7 天的临时文件
    find /tmp/openclaw -name "*.tmp" -mtime +7 -delete 2>/dev/null && count=$((count + $(find /tmp/openclaw -name "*.tmp" -mtime +7 2>/dev/null | wc -l))) || true
    find /tmp/openclaw -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    log "Temp files cleanup: done"
}

# 主函数
main() {
    log "=== Memory cleanup started ==="
    
    cleanup_daily_memories
    cleanup_cost_tracker
    cleanup_heartbeat_state
    cleanup_temp_files
    
    log "=== Memory cleanup completed ==="
    
    # 输出摘要
    echo "Memory cleanup completed at $(date -Iseconds)"
}

main "$@"
