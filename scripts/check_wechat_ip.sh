#!/bin/bash
# 微信公众号推送前检测：获取 Access Token + 验证 IP 白名单
# 如果 IP 变了，返回新 IP 提示

APPID="wx97bc84bb54232e27"
SECRET="032564217cfc2fc954e53752a7f68da3"

RESULT=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${APPID}&secret=${SECRET}")

# 检查是否成功
TOKEN=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ]; then
    echo "OK"
    echo "$TOKEN"
else
    # 提取错误信息和新 IP
    echo "$RESULT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('errcode') == 40164:
    msg = d.get('errmsg','')
    # 提取 IP
    import re
    ips = re.findall(r'\d+\.\d+\.\d+\.\d+', msg)
    if ips:
        print(f'⚠️ 公众号 IP 白名单失效！新 IP：{ips[0]}')
        print('请去以下链接更新 IP 白名单：')
        print('https://developers.weixin.qq.com/platform')
    else:
        print(f'ERROR:{msg}')
else:
    print(f'ERROR:{json.dumps(d)}')
"
fi
