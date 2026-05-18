#!/bin/bash
# OpenClaw 综合安全审计脚本
# 功能：安全检查 + 配置监控 + 登录审计 + 漏洞扫描 + mihomo 代理检查
# 输出：JSON 格式，方便解析

OPENCLAW_DIR="$HOME/.openclaw"
AUDIT_LOG="$OPENCLAW_DIR/audit/audit_$(date +%Y%m%d_%H%M%S).json"
LAST_CONFIG="$OPENCLAW_DIR/audit/last_config_hash.txt"

mkdir -p "$OPENCLAW_DIR/audit"

ISSUES="[]"
WARNINGS="[]"
INFO="[]"

add_issue() {
    ISSUES=$(echo "$ISSUES" | python3 -c "import sys,json; d=json.load(sys.stdin); d.append('$1'); print(json.dumps(d))");
}
add_warning() {
    WARNINGS=$(echo "$WARNINGS" | python3 -c "import sys,json; d=json.load(sys.stdin); d.append('$1'); print(json.dumps(d))");
}
add_info() {
    INFO=$(echo "$INFO" | python3 -c "import sys,json; d=json.load(sys.stdin); d.append('$1'); print(json.dumps(d))");
}

echo "===== OpenClaw 安全审计 ====="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# ===== 1. 定时安全审计 =====
echo "[1/6] 安全配置检查..."

# 凭证目录权限
CREDS_PERM=$(stat -c %a "$OPENCLAW_DIR/credentials" 2>/dev/null)
if [ "$CREDS_PERM" != "700" ]; then
    add_issue "凭证目录权限不安全: $CREDS_PERM (应为700)"
    echo " ❌ 凭证目录权限: $CREDS_PERM"
else
    add_info "凭证目录权限正常: 700"
    echo " ✅ 凭证目录权限: 700"
fi

# Gateway 绑定
BIND_MODE=$(python3 -c "import json; c=json.load(open('$OPENCLAW_DIR/openclaw.json')); print(c.get('gateway',{}).get('bind','unknown'))" 2>/dev/null)
if [ "$BIND_MODE" = "lan" ] || [ "$BIND_MODE" = "auto" ]; then
    add_issue "Gateway 绑定: $BIND_MODE (应为 loopback)"
    echo " ❌ Gateway 绑定: $BIND_MODE"
else
    add_info "Gateway 绑定: $BIND_MODE"
    echo " ✅ Gateway 绑定: $BIND_MODE"
fi

# ===== 2. 配置变更监控 =====
echo ""
echo "[2/6] 配置变更检测..."

CURRENT_HASH=$(sha256sum "$OPENCLAW_DIR/openclaw.json" 2>/dev/null | awk '{print $1}')
if [ -f "$LAST_CONFIG" ]; then
    LAST_HASH=$(cat "$LAST_CONFIG")
    if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
        add_warning "配置文件已变更! 上次: ${LAST_HASH:0:12}... 当前: ${CURRENT_HASH:0:12}..."
        echo " ⚠️ 配置文件已变更"
    else
        add_info "配置文件未变更"
        echo " ✅ 配置文件未变更"
    fi
else
    add_info "首次记录配置哈希"
    echo " ℹ️ 首次记录配置哈希"
fi
echo "$CURRENT_HASH" > "$LAST_CONFIG"

# ===== 3. 登录/消息审计 =====
echo ""
echo "[3/6] 通道状态审计..."

# 检查各通道状态
for channel in telegram feishu openclaw-weixin; do
    STATUS=$(openclaw status 2>/dev/null | grep -i "$channel" | head -1)
    if echo "$STATUS" | grep -qi "ON.*OK"; then
        add_info "$channel: 在线正常"
        echo " ✅ $channel: 在线正常"
    elif echo "$STATUS" | grep -qi "ON"; then
        add_warning "$channel: 已启用但状态异常"
        echo " ⚠️ $channel: 状态异常"
    else
        add_info "$channel: 未启用"
        echo " ➖ $channel: 未启用"
    fi
done

# 检查最近的异常登录
RECENT_ERRORS=$(tail -500 "$OPENCLAW_DIR"/../tmp/openclaw/openclaw-$(date +%Y-%m-%d).log 2>/dev/null | grep -ciE "error|fail|reject|denied" || echo 0)
if [ "$RECENT_ERRORS" -gt 10 ]; then
    add_warning "最近日志中有 $RECENT_ERRORS 条错误记录"
    echo " ⚠️ 最近日志错误数: $RECENT_ERRORS"
else
    add_info "最近日志错误数: $RECENT_ERRORS"
    echo " ✅ 最近日志错误数: $RECENT_ERRORS"
fi

# ===== 4. 服务状态检查 =====
echo ""
echo "[4/6] 服务状态检查..."

# 检查 mihomo 代理（检查 user service）
MIHOMO_STATUS=$(systemctl --user is-active mihomo 2>/dev/null)
if [ "$MIHOMO_STATUS" = "active" ]; then
    add_info "mihomo: 运行正常"
    echo " ✅ mihomo: 运行正常"
    
    # 获取当前版本
    MIHOMO_VER=$(/home/liyang/.local/bin/mihomo -v 2>/dev/null | head -1)
    echo "   当前版本: $MIHOMO_VER"
    
    # 检查 GitHub 最新版本
    LATEST_VER=$(curl -s https://api.github.com/repos/MetaCubeX/mihomo/releases/latest 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('tag_name','unknown'))" 2>/dev/null)
    if [ "$LATEST_VER" != "unknown" ]; then
        echo "   最新版本: $LATEST_VER"
        # 比较版本
        CURRENT_TAG=$(echo "$MIHOMO_VER" | grep -oP 'v[\d.]+' | head -1)
        if [ "$CURRENT_TAG" = "$LATEST_VER" ]; then
            add_info "mihomo: 已是最新版本 ($CURRENT_TAG)"
            echo "   ✅ 已是最新版本"
        else
            add_warning "mihomo: 发现新版本 $LATEST_VER (当前: $CURRENT_TAG)"
            echo "   ⚠️ 发现新版本: $LATEST_VER"
        fi
    else
        add_info "mihomo: 无法获取最新版本信息"
        echo "   ⚠️ 无法获取最新版本信息"
    fi
    
    # 代理测速 (3秒超时)
    echo "   测试代理连接..."
    SPEED_TEST=$(curl -s -m 3 -o /dev/null -w "%{time_total}" --proxy http://127.0.0.1:7890 https://api.github.com/ 2>/dev/null)
    if [ $? -eq 0 ]; then
        add_info "mihomo: 代理正常 (${SPEED_TEST}s)"
        echo "   ✅ 代理连接正常 (${SPEED_TEST}s)"
    else
        add_issue "mihomo: 代理连接失败"
        echo "   ❌ 代理连接失败"
    fi
else
    add_issue "mihomo: 未运行 (状态: $MIHOMO_STATUS)"
    echo " ❌ mihomo: 未运行"
fi

# Home Assistant 已卸载，跳过检查
add_info "Home Assistant: 已卸载"
echo " ➖ Home Assistant: 已卸载"

# ===== 5. 版本与漏洞检查 =====
echo ""
echo "[5/6] 版本与漏洞检查..."

CURRENT_VER=$(openclaw --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+[-\w]*' | head -1)
echo " 当前版本: $CURRENT_VER"
add_info "当前版本: $CURRENT_VER"

# 检查是否有更新
UPDATE_CHECK=$(openclaw update status 2>/dev/null | grep -i "update.*available\|up to date")
if echo "$UPDATE_CHECK" | grep -qi "available"; then
    add_warning "有新版本可用"
    echo " ⚠️ 有新版本可用"
else
    add_info "已是最新版本"
    echo " ✅ 已是最新版本"
fi

# 检查插件版本是否锁定
PINNED=$(python3 -c "
import json
c = json.load(open('$OPENCLAW_DIR/openclaw.json'))
plugins = c.get('plugins',{}).get('entries',{})
unpinned = [k for k,v in plugins.items() if isinstance(v.get('version',''), str) and not v.get('version','')]
if unpinned:
    print('UNPINNED:' + ','.join(unpinned))
else:
    print('ALL_PINNED')
" 2>/dev/null)
if echo "$PINNED" | grep -q "UNPINNED"; then
    PLUGINS=$(echo "$PINNED" | sed 's/UNPINNED://')
    add_warning "插件版本未锁定: $PLUGINS"
    echo " ⚠️ 插件未锁定版本: $PLUGINS"
else
    add_info "插件版本已锁定"
    echo " ✅ 插件版本已锁定"
fi

# ===== 6. 生成报告 =====
echo ""
echo "[6/6] 生成审计报告..."
echo ""

ISSUE_COUNT=$(echo "$ISSUES" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
WARN_COUNT=$(echo "$WARNINGS" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")

echo "发现: $ISSUE_COUNT 个问题, $WARN_COUNT 个警告"

# 保存 JSON 报告
python3 << PYEOF
import json
report = {
    "timestamp": "$(date -Iseconds)",
    "version": "$CURRENT_VER",
    "issues": $ISSUES,
    "warnings": $WARNINGS,
    "info": $INFO,
    "issue_count": $ISSUE_COUNT,
    "warning_count": $WARN_COUNT
}
with open("$AUDIT_LOG", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)
print("报告已保存: $AUDIT_LOG")
PYEOF

# 如果有问题，输出需要通知的内容
if [ "$ISSUE_COUNT" -gt 0 ]; then
    echo ""
    echo "🚨 需要通知老板的问题:"
    echo "$ISSUES" | python3 -c "import sys,json; [print(f' - {i}') for i in json.load(sys.stdin)]"
fi