#!/usr/bin/env python3
# 端到端验证 wechat skill：token 测试（不推送）
# secret 从环境变量读，不落盘
import os, sys, json, requests

sys.path.insert(0, '/home/liyang/.openclaw/workspace/skills/wechat-article-auto/scripts')

app_id = os.environ.get('WECHAT_APPID_A', 'wx97bc84bb54232e27')
secret = os.environ.get('WECHAT_APPSECRET_A')
if not secret:
    # 从 .env 加载（key=value 格式）
    env_path = '/home/liyang/.openclaw/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith('WECHAT_APPSECRET_A='):
                    secret = line.split('=', 1)[1]
                elif line.startswith('WECHAT_APPID_A='):
                    app_id = line.split('=', 1)[1]

if not secret:
    print('[FAIL] WECHAT_APPSECRET_A 未设置（环境变量和 .env 都没有）')
    sys.exit(1)

url = (
    'https://api.weixin.qq.com/cgi-bin/token'
    '?grant_type=client_credential'
    '&appid=' + app_id +
    '&secret=' + secret
)
r = requests.get(url, timeout=15).json()
if 'access_token' in r:
    print('[OK] token OK - skill ready (ip whitelist passed)')
else:
    err = r.get('errcode')
    msg = r.get('errmsg', '')
    print('[FAIL]', err, msg)
    if err == 40164:
        import re
        m = re.search(r'invalid ip ([0-9.]+)', msg)
        if m:
            print('[HINT] 需要把这个 IP 加入公众号白名单:', m.group(1))
    elif err == 40125:
        print('[HINT] app_secret 已失效，需要去微信公众号后台重新生成')