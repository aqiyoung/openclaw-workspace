import json, urllib.request

with open('/tmp/wx_secret.txt', 'rb') as f:
    raw = f.read()
s = raw.decode('utf-8').strip()

APPID = 'wx97bc84bb54232e27'
TOK_PFX = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid='
TOK_SUF = '&secret=***
ATOK = 'access_token='

tk = json.loads(urllib.request.urlopen(TOK_PFX + APPID + TOK_SUF + s).read().decode())['access_token']
cnt = json.loads(urllib.request.urlopen('https://api.weixin.qq.com/cgi-bin/material/get_materialcount?' + ATOK + tk).read().decode())
print('当前素材统计:')
for k, v in cnt.items():
    print('  ' + k + ': ' + str(v))