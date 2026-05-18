#!/bin/bash
# 检查小米摄像头移动侦测，有新消息推微信

STATE_FILE="/tmp/ha_camera_last_msg.txt"
HA_URL="http://127.0.0.1:8123"

# 获取 HA token
HA_TOKEN=$(cat /tmp/ha_token.txt 2>/dev/null)
if [ -z "$HA_TOKEN" ]; then
    exit 0
fi

# 获取摄像头消息
MSG=$(curl -s "$HA_URL/api/states/sensor.mi_29423116_message" \
    -H "Authorization: Bearer $HA_TOKEN" 2>/dev/null)

TITLE=$(echo "$MSG" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('title',''))" 2>/dev/null)
CONTENT=$(echo "$MSG" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('content',''))" 2>/dev/null)
IS_NEW=$(echo "$MSG" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('is_new',0))" 2>/dev/null)
TIMESTAMP=$(echo "$MSG" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('timestamp',''))" 2>/dev/null)

# 检查是否是新消息
LAST_MSG=$(cat "$STATE_FILE" 2>/dev/null)

if [ "$IS_NEW" = "1" ] && [ "$TITLE" != "$LAST_MSG" ] && [ -n "$TITLE" ]; then
    echo "$TITLE" > "$STATE_FILE"
    echo "📷 摄像头告警: $CONTENT - $TITLE ($TIMESTAMP)"
else
    echo "NO_REPLY"
fi
