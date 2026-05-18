#!/bin/bash
# 智能家居监控通知脚本 - 零 token 消耗
# 由 systemd timer 调用，直接通过 openclaw message send 推送

RESULT=$(bash /home/liyang/.openclaw/workspace/scripts/smart_home_local.sh)

if [ "$RESULT" != "NO_REPLY" ] && [ -n "$RESULT" ]; then
    openclaw message send --channel openclaw-weixin --message "$RESULT" 2>/dev/null
fi
