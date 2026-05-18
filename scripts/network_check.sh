#!/bin/bash
# network_check.sh - 网络状态检测工具
# 功能：IP查询、代理检测、DNS泄露、连通性、mihomo状态、网站分流

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

TIMEOUT=8
PROXY="http://127.0.0.1:7890"
MIHOMO_API="http://127.0.0.1:9090"

check_cmd() { command -v "$1" >/dev/null 2>&1; }

http_direct() {
    curl -s --max-time "$TIMEOUT" --noproxy '*' "$1" 2>/dev/null
}

http_proxy() {
    curl -s --max-time "$TIMEOUT" --proxy "$PROXY" "$1" 2>/dev/null
}

json_get() {
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('$1',''))" 2>/dev/null
}

print_header() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}"; }
print_ok() { echo -e "  ${GREEN}✅ $1${NC}"; }
print_warn() { echo -e "  ${YELLOW}⚠️  $1${NC}"; }
print_err() { echo -e "  ${RED}❌ $1${NC}"; }
print_info() { echo -e "  ${CYAN}ℹ️  $1${NC}"; }

# ===== 1. 出口 IP =====
check_exit_ip() {
    print_header "出口 IP"
    
    # 直连 IP
    DIRECT_RAW=$(http_direct "http://ip-api.com/json/?fields=query,country,city,isp,org")
    DIRECT_IP=$(echo "$DIRECT_RAW" | json_get "query")
    if [ -n "$DIRECT_IP" ] && [ "$DIRECT_IP" != "None" ]; then
        D_COUNTRY=$(echo "$DIRECT_RAW" | json_get "country")
        D_CITY=$(echo "$DIRECT_RAW" | json_get "city")
        D_ISP=$(echo "$DIRECT_RAW" | json_get "isp")
        D_ORG=$(echo "$DIRECT_RAW" | json_get "org")
        print_ok "直连: ${DIRECT_IP}"
        print_info "${D_COUNTRY} ${D_CITY} | ${D_ISP}"
        [ -n "$D_ORG" ] && [ "$D_ORG" != "None" ] && [ "$D_ORG" != "$D_ISP" ] && print_info "组织: ${D_ORG}"
    else
        print_err "直连 IP 获取失败"
    fi
    
    # 代理 IP
    PROXY_RAW=$(http_proxy "http://ip-api.com/json/?fields=query,country,city,isp,org")
    PROXY_IP=$(echo "$PROXY_RAW" | json_get "query")
    if [ -n "$PROXY_IP" ] && [ "$PROXY_IP" != "None" ]; then
        P_COUNTRY=$(echo "$PROXY_RAW" | json_get "country")
        P_CITY=$(echo "$PROXY_RAW" | json_get "city")
        P_ISP=$(echo "$PROXY_RAW" | json_get "isp")
        print_ok "代理: ${PROXY_IP}"
        print_info "${P_COUNTRY} ${P_CITY} | ${P_ISP}"
    else
        print_err "代理不可用 (${PROXY})"
    fi
    
    # IP 对比
    if [ -n "$DIRECT_IP" ] && [ -n "$PROXY_IP" ]; then
        if [ "$DIRECT_IP" = "$PROXY_IP" ]; then
            print_warn "代理 IP 与直连相同，代理可能未生效"
        else
            print_ok "代理正常（IP 不同）"
        fi
    fi
}

# ===== 2. 连通性 =====
check_connectivity() {
    print_header "连通性"
    
    # Ping 测试
    declare -A PING_OK PING_MS
    for target in "8.8.8.8" "1.1.1.1" "114.114.114.114"; do
        if ping -c 1 -W 3 "$target" >/dev/null 2>&1; then
            PING_OK[$target]=1
            PING_MS[$target]=$(ping -c 1 -W 3 "$target" 2>/dev/null | grep 'time=' | grep -oP 'time=\K[\d.]+' || echo "?")
        else
            PING_OK[$target]=0
            PING_MS[$target]="timeout"
        fi
    done
    
    echo -e "  ${CYAN}Ping:${NC}"
    for target in "8.8.8.8:Google" "1.1.1.1:Cloudflare" "114.114.114.114:国内"; do
        ip="${target%%:*}"
        name="${target##*:}"
        if [ "${PING_OK[$ip]}" = "1" ]; then
            print_ok "${name} (${ip}): ${PING_MS[$ip]}ms"
        else
            print_err "${name} (${ip}): 不通"
        fi
    done
    
    # HTTPS
    echo -e "  ${CYAN}HTTPS:${NC}"
    for site in "https://www.baidu.com" "https://www.google.com" "https://github.com"; do
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 6 --noproxy '*' "$site" 2>/dev/null || echo "000")
        if [ "$STATUS" = "200" ]; then
            print_ok "${site}: ${STATUS}"
        else
            print_warn "${site}: ${STATUS}"
        fi
    done
}

# ===== 3. mihomo =====
check_mihomo() {
    print_header "mihomo"
    
    if ! pgrep -f mihomo >/dev/null 2>&1; then
        print_err "未运行"
        return
    fi
    
    PID=$(pgrep -f mihomo | head -1)
    MEM=$(ps -p "$PID" -o rss= 2>/dev/null | awk '{printf "%.0f MB", $1/1024}')
    UPTIME=$(ps -p "$PID" -o etime= 2>/dev/null | xargs)
    print_ok "运行中 (PID:$PID ${MEM} ${UPTIME})"
    
    if ! curl -s --max-time 3 "${MIHOMO_API}/version" >/dev/null 2>&1; then
        print_err "API 无响应"
        return
    fi
    
    VERSION=$(curl -s "${MIHOMO_API}/version" 2>/dev/null | json_get "version")
    print_ok "版本: ${VERSION}"
    
    PROXIES=$(curl -s "${MIHOMO_API}/proxies" 2>/dev/null)
    if [ -n "$PROXIES" ]; then
        # 当前节点
        CURRENT=$(echo "$PROXIES" | python3 -c "
import sys,json
d=json.load(sys.stdin)
p=d.get('proxies',{})
for name,g in p.items():
    if name=='GLOBAL': continue
    if isinstance(g,dict) and g.get('type')=='Selector':
        now=g.get('now','')
        all_list=g.get('all',[])
        real=[x for x in all_list if x not in ('DIRECT','REJECT','PASS','GLOBAL')]
        print(f'{name}→{now} ({len(real)}节点)')
" 2>/dev/null)
        [ -n "$CURRENT" ] && print_ok "当前: ${CURRENT}"
        
        # 可用节点数
        STATS=$(echo "$PROXIES" | python3 -c "
import sys,json
d=json.load(sys.stdin)
p=d.get('proxies',{})
exclude={'GLOBAL','DIRECT','REJECT','PASS'}
total=0; alive=0
for name,pr in p.items():
    if name in exclude or not isinstance(pr,dict): continue
    if 'all' in name: continue
    total+=1
    h=pr.get('history',[])
    if h and h[-1].get('delay',0)>0: alive+=1
print(f'{alive}/{total}')
" 2>/dev/null)
        [ -n "$STATS" ] && print_ok "可用: ${STATS}"
    fi
    
    # 配置
    CONFIG="$HOME/.config/mihomo/config.yaml"
    if [ -f "$CONFIG" ]; then
        SUB=$(grep -A5 "proxy-providers" "$CONFIG" | grep "interval:" | head -1 | awk '{print $2}')
        HEALTH=$(grep -A10 "health-check" "$CONFIG" | grep "interval:" | head -1 | awk '{print $2}')
        [ -n "$SUB" ] && print_info "订阅: $((SUB/3600))h | 健康检查: $((HEALTH/60))min"
    fi
}

# ===== 4. DNS 泄露 =====
check_dns_leak() {
    print_header "DNS 泄露"
    
    if ! check_cmd dig; then
        print_warn "dig 未安装"
        return
    fi
    
    OPENDNS=$(dig +short +time=5 myip.opendns.com @resolver1.opendns.com 2>/dev/null | head -1)
    [ -n "$OPENDNS" ] && print_ok "OpenDNS: ${OPENDNS}" || print_warn "OpenDNS: 超时"
    
    CLOUDFLARE=$(dig +short +time=5 whoami.akamai.net @1.1.1.1 2>/dev/null | head -1)
    [ -n "$CLOUDFLARE" ] && print_ok "Cloudflare: ${CLOUDFLARE}" || print_warn "Cloudflare: 超时"
    
    if check_cmd resolvectl; then
        DNS_LIST=$(resolvectl status 2>/dev/null | grep 'DNS Servers' | head -3 | awk '{print $3}' | tr '\n' ', ')
        [ -n "$DNS_LIST" ] && print_info "本机 DNS: ${DNS_LIST}"
    fi
}

# ===== 5. 网站分流 =====
check_routing() {
    print_header "网站分流"
    
    # 代理出口 IP
    ROUTE_RAW=$(http_proxy "http://ip-api.com/json/?fields=query,country,city,isp")
    ROUTE_IP=$(echo "$ROUTE_RAW" | json_get "query")
    if [ -n "$ROUTE_IP" ] && [ "$ROUTE_IP" != "None" ]; then
        R_COUNTRY=$(echo "$ROUTE_RAW" | json_get "country")
        R_CITY=$(echo "$ROUTE_RAW" | json_get "city")
        R_ISP=$(echo "$ROUTE_RAW" | json_get "isp")
        print_ok "代理出口: ${ROUTE_IP} | ${R_COUNTRY} ${R_CITY} | ${R_ISP}"
    fi
    
    echo -e "  ${CYAN}访问测试:${NC}"
    
    # 百度（直连）
    T=$(curl -s -o /dev/null -w '%{time_total}' --max-time 6 --noproxy '*' "https://www.baidu.com" 2>/dev/null || echo "99")
    MS=$(python3 -c "print(int(${T}*1000))" 2>/dev/null || echo "?")
    [ "$MS" != "?" ] && [ "$MS" -lt 3000 ] && print_ok "百度: ${MS}ms (直连)" || print_warn "百度: ${MS}ms"
    
    # Google（代理）
    T=$(curl -s -o /dev/null -w '%{time_total}' --max-time 8 --proxy "$PROXY" "https://www.google.com" 2>/dev/null || echo "99")
    MS=$(python3 -c "print(int(${T}*1000))" 2>/dev/null || echo "?")
    [ "$MS" != "?" ] && [ "$MS" -lt 5000 ] && print_ok "Google: ${MS}ms (代理)" || print_warn "Google: ${MS}ms"
    
    # GitHub（代理）
    T=$(curl -s -o /dev/null -w '%{time_total}' --max-time 8 --proxy "$PROXY" "https://github.com" 2>/dev/null || echo "99")
    MS=$(python3 -c "print(int(${T}*1000))" 2>/dev/null || echo "?")
    [ "$MS" != "?" ] && [ "$MS" -lt 5000 ] && print_ok "GitHub: ${MS}ms (代理)" || print_warn "GitHub: ${MS}ms"
}

# ===== 主程序 =====
main() {
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   网络状态检测 $(date '+%H:%M:%S')                  ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    
    check_exit_ip
    check_connectivity
    check_mihomo
    check_dns_leak
    check_routing
    
    echo ""
}

main "$@"
