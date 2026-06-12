#!/bin/bash
# Claude Code wrapper — 带缓存的 model-sync
# 装这个文件：ln -s scripts/claude-wrapper.sh ~/.local/bin/claude
# 或者把内容加到 ~/.bashrc
#
# 作用：让 claude() 命令自动用 OpenClaw 配置的主模型，
# 通过本地 Anthropic→OpenAI proxy (port 9876) 调用真 Claude

claude() {
    _config="/home/liyang/.openclaw/openclaw.json"
    _cache="/tmp/model-sync-cache.sh"
    _config_mtime=$(stat -c %Y "$_config" 2>/dev/null)
    _cache_mtime=$(stat -c %Y "$_cache" 2>/dev/null)

    if [ ! -f "$_cache" ] || [ "$_config_mtime" -gt "$_cache_mtime" ]; then
        # 调 model-sync.sh 生成主模型环境变量
        source /home/liyang/.openclaw/workspace/scripts/model-sync.sh 2>/dev/null

        # Claude Code 走本地 Anthropic→OpenAI proxy (lidlid 真 Claude)
        python3 -c "
import json, os
c = json.load(open('$_config'))
proxy_url = 'http://127.0.0.1:9876'
env_path = os.path.expanduser('~/.openclaw/.env')
lidlid_key = None
if os.path.exists(env_path):
    for line in open(env_path):
        if line.startswith('LIDLID_API_KEY='):
            lidlid_key = line.strip().split('=', 1)[1]
            break
primary = c.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', 'lidlid-cn/claude-opus-4.8')
model_id = primary.split('/', 1)[-1]
# Claude code 0.139.0 需要横线命名（claude-opus-4-8），不是点（claude-opus-4.8）
if model_id == 'claude-opus-4.8':
    model_id = 'claude-opus-4-8'
with open('/tmp/claude-anthropic-env.sh', 'w') as f:
    f.write(f\"export ANTHROPIC_BASE_URL='{proxy_url}'\\n\")
    f.write(f\"export ANTHROPIC_API_KEY='{lidlid_key or 'dummy'}'\\n\")
    f.write(f\"export ANTHROPIC_AUTH_TOKEN='{lidlid_key or 'dummy'}'\\n\")
    f.write(f\"export ANTHROPIC_MODEL='{model_id}'\\n\")
    f.write(f\"export ANTHROPIC_SMALL_FAST_MODEL='{model_id}'\\n\")
    f.write(f\"export ANTHROPIC_DEFAULT_SONNET_MODEL='{model_id}'\\n\")
    f.write(f\"export ANTHROPIC_DEFAULT_OPUS_MODEL='{model_id}'\\n\")
print(f'claude → local proxy → {primary}')
" 2>/dev/null
        [ -f /tmp/claude-anthropic-env.sh ] && source /tmp/claude-anthropic-env.sh
    else
        source "$_cache"
    fi
    /home/liyang/.nvm/versions/node/v24.15.0/bin/claude "$@"
}

# Codex wrapper — 复用 claude() 的缓存
codex() {
    _cache="/tmp/model-sync-cache.sh"
    [ -f "$_cache" ] && source "$_cache"
    command codex --dangerously-bypass-approvals-and-sandbox "$@"
}
