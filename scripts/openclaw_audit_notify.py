#!/usr/bin/env python3
"""OpenClaw 审计 + 通知 wrapper
跑审计脚本，如果有问题则通知老板
"""
import subprocess, json, os, sys

AUDIT_SCRIPT = "/home/liyang/.openclaw/workspace/scripts/openclaw_audit.py"

# 跑审计
result = subprocess.run(
    ["python3", AUDIT_SCRIPT],
    capture_output=True, text=True, timeout=60
)

# 读取最新审计报告
audit_dir = os.path.expanduser("~/.openclaw/audit")
reports = sorted([
    f for f in os.listdir(audit_dir)
    if f.startswith("audit_") and f.endswith(".json")
]) if os.path.exists(audit_dir) else []

if not reports:
    sys.exit(0)

latest = os.path.join(audit_dir, reports[-1])
with open(latest) as f:
    report = json.load(f)

issue_count = report.get("issue_count", 0)
warning_count = report.get("warning_count", 0)

if issue_count == 0 and warning_count == 0:
    # 全绿，不用通知
    sys.exit(0)

# 构建通知消息
msg_parts = ["🔍 OpenClaw 定时审计报告\n"]
msg_parts.append(f"时间: {report['timestamp'][:19]}")
msg_parts.append(f"版本: {report.get('version', 'unknown')}")

if issue_count > 0:
    msg_parts.append(f"\n❌ 发现 {issue_count} 个问题:")
    for i in report.get("issues", []):
        msg_parts.append(f"  - {i}")

if warning_count > 0:
    msg_parts.append(f"\n⚠️ {warning_count} 个警告:")
    for w in report.get("warnings", []):
        msg_parts.append(f"  - {w}")

notification = "\n".join(msg_parts)

# 写入通知文件，由 cron 或 heartbeat 读取发送
notify_file = os.path.expanduser("~/.openclaw/audit/pending_notification.txt")
with open(notify_file, "w") as f:
    f.write(notification)

print(f"审计完成，发现 {issue_count} 个问题 + {warning_count} 个警告")
print(f"通知已写入: {notify_file}")
