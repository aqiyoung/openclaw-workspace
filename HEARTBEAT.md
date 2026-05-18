# HEARTBEAT.md

## cost_tracker 记录
每次心跳时，调用 `session_status` 获取当前 token 消耗，写入 `~/.openclaw/cost_tracker/YYYY-MM-DD.jsonl`。

写入格式：
```json
{"ts": "2026-04-02T20:20:00+08:00", "sessionKey": "agent:main:main", "model": "...", "tokensIn": 15234, "tokensOut": 8912, "tokensCached": 12450, "contextUsed": 80226, "contextTotal": 131072, "costUsd": 0.02}
```

**注意**：只记录主会话（agent:main:main），不记录子会话。

## history-log 记录
每次心跳时，追加一条执行记录到 `~/.openclaw/history/YYYY-MM-DD.jsonl`。

写入格式：
```json
{"ts": "2026-04-02T22:12:00+08:00", "action": "optimize", "detail": "创建 skill-router scoring 配置", "status": "done"}
```

**注意**：只在有重要操作时追加，不要每条消息都写。

## 审计通知检查
检查 `~/.openclaw/audit/pending_notification.txt` 是否存在。如果存在：
1. 读取内容
2. 通过当前通道发送给老板
3. 删除该文件
4. 回复 HEARTBEAT_OK

## 定时器健康检查
每 10 次心跳检查一次以下定时器是否正常运行：
- openclaw-restart-notify.timer

用 `systemctl --user list-timers` 检查。如果发现丢失，立即重建并通知老板。

## Headless Chromium 保活检查
每次心跳时检查 CDP 端口 9222 是否响应：
```bash
bash ~/.openclaw/workspace/scripts/ensure-headless.sh
```
如果 Chromium 挂了，自动重启。如果重启失败，通知老板。

## 上下文预算监控
每次心跳时，用 session_status 获取 context 使用率，然后调用 `scripts/context_budget.sh`：
```bash
bash ~/.openclaw/workspace/scripts/context_budget.sh <used_pct>
```
- 超过 70%：黄色警告（仅记录，不推消息）
- 超过 80%：橙色告警（推微信）
- 超过 90%：红色紧急（推微信 + 建议清理记忆）

同时写入 `/tmp/openclaw/context_budget.json`，Jarvis 面板可读取展示。

## 智能记忆提取（每 3 次心跳）
检查 `~/self-improving/heartbeat-state.md` 中的 `last_memory_extract` 字段。
如果距上次提取超过 3 次心跳：
1. 回顾最近 10 条对话记录
2. 提取值得长期记忆的信息（偏好、决策、关键事实）
3. 写入 `memory/YYYY-MM-DD.md`（带 frontmatter）
4. 更新 heartbeat-state.md 中的 `last_memory_extract`

**提取规则**：
- 只提取用户明确表达的偏好、重要决策、关键事实
- 不提取临时信息（天气、任务状态）、可推导信息
- 先检查 MEMORY.md 是否已有类似内容，避免重复

## 微压缩清理（每天一次）
检查 `~/self-improving/heartbeat-state.md` 中的 `last_memory_cleanup` 字段。
如果距上次清理超过 24 小时：
```bash
bash ~/.openclaw/workspace/scripts/memory_cleanup.sh
```
- 清理 30 天前的日期命名记忆文件（提取关键行，丢弃过程数据）
- 清理 7 天前的费用追踪文件
- 清理 7 天前的临时文件

## Self-Improving Check
- Read `./skills/self-improving/heartbeat-rules.md`
- Use `~/self-improving/heartbeat-state.md` for last-run markers and action notes
- If no file inside `~/self-improving/` changed since the last reviewed change, return `HEARTBEAT_OK`

## 设备配对请求检查
每次心跳时检查是否有待审批的设备配对请求：
```bash
openclaw devices list --json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    pending = [d for d in data.get('devices', []) if d.get('status') == 'pending']
    for p in pending:
        print(f"{p.get('id')} | {p.get('name', 'unknown')} | {p.get('role', 'operator')}")
except:
    pass
"
```
如果有 pending 设备，通过 Telegram 通知老板：
"🔐 有新的 Web 控制台设备配对请求：
{设备信息}

回复「批准设备」我来执行 approve"

**注意**：不要自动批准，必须等老板确认。
