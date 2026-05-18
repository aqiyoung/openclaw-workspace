#!/bin/bash
# GitHub 热点项目每日同步脚本
# 功能:搜索 GitHub 热点项目并写入 IMA 知识库
# 依赖:gh CLI(已认证)、jq、python3

set -e

# Load environment variables from .env
[ -f "$HOME/.openclaw/.env" ] && source "$HOME/.openclaw/.env"

KB_ID="ajHFthmc6DI14j_T_w6RfwiQoO26jwfmZklNwoPR0ag="
LOG_FILE="/tmp/github_sync_$(date +%Y%m%d).log"
TEMP_DIR=$(mktemp -d)

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

check_dependencies() {
    log "检查依赖工具..."
    for cmd in gh jq python3; do
        if ! command -v "$cmd" &> /dev/null; then
            log "错误:缺少依赖工具 $cmd"
            exit 1
        fi
    done
    # 验证 gh 已认证
    if ! gh auth status &>/dev/null; then
        log "错误:gh CLI 未认证,请运行 gh auth login"
        exit 1
    fi
    log "依赖检查完成"
}

check_github_rate_limit() {
    local limit_info
    limit_info=$(gh api rate_limit --jq '.resources.core.remaining' 2>/dev/null || echo "0")
    log "GitHub API 剩余配额: $limit_info"
    if [ "$limit_info" -lt 3 ] 2>/dev/null; then
        log "警告:GitHub API 配额不足,跳过本次同步"
        return 1
    fi
    return 0
}

search_github_projects() {
    log "开始搜索 GitHub 热点项目..."

    local since_date
    since_date=$(date -d '3 days ago' '+%Y-%m-%d' 2>/dev/null || date -v-3d '+%Y-%m-%d' 2>/dev/null)

    # 用 gh api 搜索,自动带认证
    local response
    response=$(gh api "search/repositories?q=created:>${since_date}+stars:>100&sort=stars&order=desc&per_page=10" 2>/dev/null)

    if echo "$response" | jq -e '.items' > /dev/null 2>&1; then
        echo "$response" > "$TEMP_DIR/github_response.json"
        local count
        count=$(echo "$response" | jq '.items | length')
        local total
        total=$(echo "$response" | jq '.total_count // 0')
        log "搜索完成,找到 $count 个项目(总计 $total)"
    else
        log "GitHub API 返回无效: $(echo "$response" | head -c 200)"
        echo '{"items":[]}' > "$TEMP_DIR/github_response.json"
        return 1
    fi
}

generate_summary() {
    log "生成项目摘要..."
    local summary_file="$TEMP_DIR/summary.md"
    local count
    count=$(jq '.items | length' "$TEMP_DIR/github_response.json" 2>/dev/null || echo "0")

    echo "# GitHub 热点项目日报 - $(date '+%Y年%m月%d日')" > "$summary_file"
    echo "" >> "$summary_file"

    if [ "$count" -eq 0 ] 2>/dev/null; then
        echo "今日暂未获取到新的热点项目。" >> "$summary_file"
        log "无项目数据"
        return 0
    fi

    echo "## 今日热门项目" >> "$summary_file"
    echo "" >> "$summary_file"

    python3 << PYEOF >> "$summary_file"
import json
with open('$TEMP_DIR/github_response.json') as f:
    data = json.load(f)
for i, item in enumerate(data.get('items', []), 1):
    name = item.get('full_name', '未知')
    desc = item.get('description', '无描述') or '无描述'
    stars = item.get('stargazers_count', 0)
    lang = item.get('language', '未知') or '未知'
    url = item.get('html_url', '#')
    print(f"### {i}. [{name}]({url})")
    print(f"- **Stars:** {stars} ⭐ | **语言:** {lang}")
    print(f"- **描述:** {desc}")
    print()
PYEOF

    log "摘要生成完成,共 $count 个项目"
}

write_to_knowledge_base() {
    log "开始写入 IMA 知识库..."

    local client_id="${IMA_OPENAPI_CLIENTID:-}"
    local api_key="${IMA_OPENAPI_APIKEY:-}"

    if [ -z "$client_id" ] && [ -f "/home/liyang/.config/ima/client_id" ]; then
        client_id=$(cat /home/liyang/.config/ima/client_id)
    fi
    if [ -z "$api_key" ] && [ -f "/home/liyang/.config/ima/api_key" ]; then
        api_key=$(cat /home/liyang/.config/ima/api_key)
    fi

    if [ -z "$client_id" ] || [ -z "$api_key" ]; then
        log "错误:未找到 IMA 凭证"
        return 1
    fi

    local title="GitHub 热点项目日报 - $(date '+%Y-%m-%d')"

    if echo "$kb_response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('code')==0 else 1)" 2>/dev/null; then
        log "成功写入 IMA 知识库"
        return 0
    else
        log "写入知识库失败: $kb_response"
        return 1
    fi

    # Step 1: Create note
    local note_response
    note_response=$(curl -s --max-time 30 -X POST \
        "https://ima.qq.com/openapi/note/v1/import_doc" \
        -H "Content-Type: application/json" \
        -H "ima-openapi-clientid: $client_id" \
        -H "ima-openapi-apikey: $api_key" \
        -H "ima-openapi-ctx: skill_version=1.0" \
        --data-binary @"$json_file" 2>/dev/null)

    local note_id
    note_id=$(echo "$note_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('note_id',''))" 2>/dev/null)

    if [ -z "$note_id" ]; then
        log "错误:创建笔记失败: $note_response"
        return 1
    fi
    log "笔记创建成功: $note_id"

    # Step 2: Add to knowledge base
    local kb_json_file="$TEMP_DIR/kb_payload.json"
    cat > "$kb_json_file" << KBEOF
{
    "media_type": 11,
    "title": "$title",
    "knowledge_base_id": "$KB_ID",
    "note_info": {"content_id": "$note_id"}
}
KBEOF

    local kb_response
    kb_response=$(curl -s --max-time 30 -X POST \
        "https://ima.qq.com/openapi/wiki/v1/add_knowledge" \
        -H "Content-Type: application/json" \
        -H "ima-openapi-clientid: $client_id" \
        -H "ima-openapi-apikey: $api_key" \
        -H "ima-openapi-ctx: skill_version=1.0" \
        --data-binary @"$kb_json_file" 2>/dev/null)

    if echo "$kb_response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('code')==0 else 1)" 2>/dev/null; then
        log "成功写入 IMA 知识库"
        return 0
    else
        log "写入知识库失败: $kb_response"
        return 1
    fi
}"
    local api_key="${IMA_OPENAPI_APIKEY:-}"

    if [ -z "$client_id" ] && [ -f "/home/liyang/.config/ima/client_id" ]; then
        client_id=$(cat /home/liyang/.config/ima/client_id)
    fi
    if [ -z "$api_key" ] && [ -f "/home/liyang/.config/ima/api_key" ]; then
        api_key=$(cat /home/liyang/.config/ima/api_key)
    fi

    if [ -z "$client_id" ] || [ -z "$api_key" ]; then
        log "错误:未找到 IMA 凭证"
        return 1
    fi

    local title="GitHub 热点项目日报 - $(date '+%Y-%m-%d')"

    # Step 1: Create note
    local note_response
    note_response=$(curl -s --max-time 30 -X POST \
        "https://ima.qq.com/openapi/note/v1/import_doc" \
        -H "Content-Type: application/json" \
        -H "ima-openapi-clientid: $client_id" \
        -H "ima-openapi-apikey: $api_key" \
        -H "ima-openapi-ctx: skill_version=1.0" \
        -d "$(python3 -c "
import json
title = '$title'
content = open('$TEMP_DIR/summary.md').read()
print(json.dumps({'content_format': 1, 'title': title, 'content': content}))
" 2>/dev/null)" 2>/dev/null)

    local note_id
    note_id=$(echo "$note_response" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('note_id',''))" 2>/dev/null)

    if [ -z "$note_id" ]; then
        log "错误:创建笔记失败: $note_response"
        return 1
    fi
    log "笔记创建成功: $note_id"

    # Step 2: Add to knowledge base
    local kb_response
    kb_response=$(curl -s --max-time 30 -X POST \
        "https://ima.qq.com/openapi/wiki/v1/add_knowledge" \
        -H "Content-Type: application/json" \
        -H "ima-openapi-clientid: $client_id" \
        -H "ima-openapi-apikey: $api_key" \
        -H "ima-openapi-ctx: skill_version=1.0" \
        -d "$(python3 -c "
import json
print(json.dumps({
    'media_type': 11,
    'title': '$title',
    'knowledge_base_id': '$KB_ID',
    'note_info': {'content_id': '$note_id'}
}))
" 2>/dev/null)" 2>/dev/null)

    if echo "$kb_response" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('code')==0 else 1)" 2>/dev/null; then
        log "成功写入 IMA 知识库"
        return 0
    else
        log "写入知识库失败: $kb_response"
        return 1
    fi
}

main() {
    log "=== GitHub 热点项目同步开始 ==="
    check_dependencies
    check_github_rate_limit || exit 0
    search_github_projects || { log "搜索失败"; exit 1; }
    generate_summary
    write_to_knowledge_base || { log "写入失败"; exit 1; }
    local count
    count=$(jq '.items | length' "$TEMP_DIR/github_response.json" 2>/dev/null || echo "0")
    log "=== 同步完成 === 共 $count 个项目"
}

main "$@"
