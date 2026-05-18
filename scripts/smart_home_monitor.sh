#!/bin/bash
# 智能家居设备监控 - 按季节动态判断温度异常

STATE_DIR="/tmp/ha_monitor"
mkdir -p "$STATE_DIR"

# 判断是否在家
if ping -c 1 -W 2 192.168.31.220 > /dev/null 2>&1; then
    IS_HOME="true"
else
    IS_HOME="false"
fi

# 获取当前月份，设置温度阈值
MONTH=$(date +%m)
case $MONTH in
    12|01|02) # 冬季
        TEMP_LOW=10; TEMP_HIGH=30
        TEMP_LABEL="冬季"
        ;;
    03|04|05) # 春季
        TEMP_LOW=8; TEMP_HIGH=32
        TEMP_LABEL="春季"
        ;;
    06|07|08) # 夏季
        TEMP_LOW=18; TEMP_HIGH=38
        TEMP_LABEL="夏季"
        ;;
    09|10|11) # 秋季
        TEMP_LOW=10; TEMP_HIGH=32
        TEMP_LABEL="秋季"
        ;;
    *)
        TEMP_LOW=10; TEMP_HIGH=35
        TEMP_LABEL=""
        ;;
esac

# 登录 HA
HA_TOKEN=$(curl -s -X POST "http://127.0.0.1:8123/auth/login_flow" \
    -H "Content-Type: application/json" \
    -d '{"client_id":"http://127.0.0.1:8123/","handler":["homeassistant",null],"redirect_uri":"http://127.0.0.1:8123/"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['flow_id'])" 2>/dev/null)
RESULT=$(curl -s -X POST "http://127.0.0.1:8123/auth/login_flow/$HA_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"username":"threely","password":"younglee1018","client_id":"http://127.0.0.1:8123/"}' 2>/dev/null)
CODE=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result'])" 2>/dev/null)
TOKEN=$(curl -s -X POST "http://127.0.0.1:8123/auth/token" \
    -d "grant_type=authorization_code&code=$CODE&client_id=http://127.0.0.1:8123/" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

[ -z "$TOKEN" ] && exit 0

HA_URL="http://127.0.0.1:8123"
ALERTS=""

get_state() {
    curl -s "$HA_URL/api/states/$1" -H "Authorization: Bearer $TOKEN" 2>/dev/null
}

# 摄像头移动侦测（在家不推）
MSG_STATE=$(get_state "sensor.mi_29423116_message")
TITLE=$(echo "$MSG_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('title',''))" 2>/dev/null)
IS_NEW=$(echo "$MSG_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('is_new',0))" 2>/dev/null)
LAST_CAM=$(cat "$STATE_DIR/camera_last" 2>/dev/null)

if [ "$IS_NEW" = "1" ] && [ "$TITLE" != "$LAST_CAM" ] && [ -n "$TITLE" ]; then
    if [ "$IS_HOME" != "true" ]; then
        CONTENT=$(echo "$MSG_STATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('content',''))" 2>/dev/null)
        ALERTS="${ALERTS}📷 摄像头告警: ${CONTENT} - ${TITLE}\n"
    fi
    echo "$TITLE" > "$STATE_DIR/camera_last"
fi

# 温度异常检测（按季节）
TEMP=$(get_state "sensor.xiaomi_m9_0d2f_temperature" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state',''))" 2>/dev/null)
if [ -n "$TEMP" ] && [ "$TEMP" != "unavailable" ]; then
    TEMP_INT=${TEMP%.*}
    LAST_TEMP=$(cat "$STATE_DIR/last_temp" 2>/dev/null)
    if [ "$TEMP_INT" -lt "$TEMP_LOW" ] && [ "$TEMP_INT" != "$LAST_TEMP" ]; then
        ALERTS="${ALERTS}🌡️ 室内温度偏低: ${TEMP}°C（${TEMP_LABEL}，${TEMP_LOW}°C以下才算异常）\n"
    elif [ "$TEMP_INT" -gt "$TEMP_HIGH" ] && [ "$TEMP_INT" != "$LAST_TEMP" ]; then
        ALERTS="${ALERTS}🔥 室内温度偏高: ${TEMP}°C（${TEMP_LABEL}，${TEMP_HIGH}°C以上才算异常）\n"
    fi
    echo "$TEMP_INT" > "$STATE_DIR/last_temp"
fi

# 空调状态变化
check_change() {
    local entity_id="$1"
    local label="$2"
    local state_file="$STATE_DIR/$(echo $entity_id | tr '.' '_')"
    local current=$(get_state "$entity_id" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state',''))" 2>/dev/null)
    local last=$(cat "$state_file" 2>/dev/null)
    if [ -n "$current" ] && [ "$current" != "$last" ] && [ "$current" != "unavailable" ] && [ -n "$last" ]; then
        ALERTS="${ALERTS}🔔 ${label}: ${last} → ${current}\n"
    fi
    echo "$current" > "$state_file"
}

check_change "switch.xiaomi_m9_0d2f_switch_status" "空调"
check_change "switch.viomi_u26_0db6_switch_status" "热水器"

# 智能插座功耗异常
POWER=$(get_state "sensor.chuangmi_v3_b8fb_electric_power" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state','0'))" 2>/dev/null)
if [ -n "$POWER" ] && python3 -c "exit(0 if float('$POWER') > 2000 else 1)" 2>/dev/null; then
    ALERTS="${ALERTS}⚡ 智能插座功耗异常: ${POWER}W\n"
fi

# 输出
if [ -n "$ALERTS" ]; then
    HOME_TEXT="在家"
    [ "$IS_HOME" != "true" ] && HOME_TEXT="不在家"
    echo -e "🏠 智能家居 (${HOME_TEXT})\n$ALERTS"
else
    echo "NO_REPLY"
fi
