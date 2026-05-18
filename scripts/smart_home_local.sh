#!/bin/bash
# 智能家居监控 - 本地 bash 直接推送，零 token 消耗
# 配合 systemd timer 使用，每 3 分钟执行一次

STATE_DIR="/tmp/ha_monitor"
HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIzNWJiMmVlNDNjMzc0ZDdmOWQ4OTU3OTZhMGU2YzU3YyIsImlhdCI6MTc3NDgyNzg2MCwiZXhwIjoyMDkwMTg3ODYwfQ.aTV1aFqbT7-E3MiYWdRfcmjWJEx3ZqUmF9y6IUU3DQQ"
HA_URL="http://192.168.31.58:8123"
HA_STATE_FILE="/tmp/ha_monitor/ha_online"

mkdir -p "$STATE_DIR"

# 先检查 HA 是否在线（HTTP 200=正常, 401=在线但token问题, 其他=离线）
HA_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -m 5 "$HA_URL/api/" 2>/dev/null)
HA_WAS_ONLINE=$(cat "$HA_STATE_FILE" 2>/dev/null)

if [ "$HA_CHECK" = "000" ] || [ "$HA_CHECK" = "502" ] || [ "$HA_CHECK" = "503" ]; then
    # HA 真的挂了
    if [ "$HA_WAS_ONLINE" != "offline" ]; then
        echo "offline" > "$HA_STATE_FILE"
        echo -e "⚠️ Home Assistant 离线！\n状态码: ${HA_CHECK}\n请检查 NAS 上的 HA 容器"
        exit 0
    fi
    echo "NO_REPLY"
    exit 0
fi

# HA 恢复在线，如果之前是离线，通知恢复
if [ "$HA_WAS_ONLINE" = "offline" ]; then
    echo "online" > "$HA_STATE_FILE"
    echo "✅ Home Assistant 已恢复在线"
    exit 0
fi

echo "online" > "$HA_STATE_FILE"

# 如果 token 过期（401），只做连通性检查，跳过设备监控
if [ "$HA_CHECK" = "401" ]; then
    echo "NO_REPLY"
    exit 0
fi

# 判断是否在家
if ping -c 1 -W 2 192.168.31.220 > /dev/null 2>&1; then
    IS_HOME="true"
else
    IS_HOME="false"
fi

# 获取 HA 状态
get_state() {
    curl -s -m 5 -H "Authorization: Bearer $HA_TOKEN" \
        "$HA_URL/api/states/$1" 2>/dev/null
}

ALERTS=""

# 摄像头移动侦测（不在家才推）
if [ "$IS_HOME" != "true" ]; then
    CAMERA_STATE=$(get_state "binary_sensor.chuangmi_093ac1_8cc0_motion_detection" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null)
    if [ "$CAMERA_STATE" = "on" ]; then
        ALERTS="${ALERTS}📷 摄像头检测到移动\n"
    fi
fi

# 空调温度异常
AC_TEMP=$(get_state "climate.xiaomi_m9_0d2f_climate" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('attributes',{}).get('current_temperature',''))" 2>/dev/null)
if [ -n "$AC_TEMP" ] && python3 -c "t=float('$AC_TEMP'); exit(0 if t>32 or t<10 else 1)" 2>/dev/null; then
    ALERTS="${ALERTS}🌡️ 空调温度异常: ${AC_TEMP}°C\n"
fi

# 热水器状态
HEATER=$(get_state "water_heater.viomi_u26_0db6_water_heater" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null)
if [ "$HEATER" = "on" ]; then
    HOUR=$(date +%H)
    if [ "$HOUR" -ge 0 ] && [ "$HOUR" -lt 6 ]; then
        ALERTS="${ALERTS}🔥 热水器凌晨还在运行\n"
    fi
fi

# 设备状态变化
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

# 温湿度异常
TEMP=$(get_state "sensor.illumination_m_cn_4f5e_temperature" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null)
HUMI=$(get_state "sensor.illumination_m_cn_4f5e_humidity" | python3 -c "import sys,json; print(json.load(sys.stdin).get('state',''))" 2>/dev/null)
MONTH=$(date +%m)
case $MONTH in
    12|01|02) TEMP_LOW=10; TEMP_HIGH=30 ;;
    03|04|05) TEMP_LOW=8; TEMP_HIGH=32 ;;
    06|07|08) TEMP_LOW=18; TEMP_HIGH=38 ;;
    09|10|11) TEMP_LOW=10; TEMP_HIGH=32 ;;
esac
if [ -n "$TEMP" ] && python3 -c "t=float('$TEMP'); exit(0 if t<$TEMP_LOW or t>$TEMP_HIGH else 1)" 2>/dev/null; then
    ALERTS="${ALERTS}🌡️ 室温异常: ${TEMP}°C\n"
fi
if [ -n "$HUMI" ] && python3 -c "h=float('$HUMI'); exit(0 if h>80 or h<20 else 1)" 2>/dev/null; then
    ALERTS="${ALERTS}💧 湿度异常: ${HUMI}%\n"
fi

# 输出
if [ -n "$ALERTS" ]; then
    HOME_TEXT="在家"
    [ "$IS_HOME" != "true" ] && HOME_TEXT="不在家"
    echo -e "🏠 智能家居 (${HOME_TEXT})\n$ALERTS"
else
    echo "NO_REPLY"
fi
