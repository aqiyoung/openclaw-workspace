import urllib.request, json, os

appid = 'wx97bc84bb54232e27'
secret = '***'

url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=*** + secret
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req, timeout=15)
token = json.loads(resp.read())['access_token']
print('Token OK')

cover = '/tmp/kylin-v10-cover-v3.png'
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
with open(cover, 'rb') as f:
    data = f.read()
body = ('--' + boundary + '\r\nContent-Disposition: form-data; name="media"; filename="cover.png"\r\nContent-Type: image/png\r\n\r\n').encode() + data + ('\r\n--' + boundary + '--\r\n').encode()
upload_url = 'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=*** + token + '&type=image'
req = urllib.request.Request(upload_url, data=body, headers={'Content-Type': 'multipart/form-data; boundary=' + boundary})
resp = urllib.request.urlopen(req, timeout=30)
result = json.loads(resp.read())
new_id = result['media_id']
print('Upload OK: ' + new_id)

html = '<section style="padding:10px 0">'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">那天下午两点，客户把电脑搬到了会议室。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">一台戴尔 OptiPlex 3080，i5-10500，8GB 内存，512G 固态。说是要装银河麒麟 V10 SP1，替换掉原来的 Windows 10。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">麒麟 V10 镜像 U 盘已经做好了，启动盘识别正常，安装界面也不报错。分区的时候我选了默认方案——一个根分区加一个 home 分区，简单省事。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">我心想：稳了。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">四十分钟后，系统装好了，重启进桌面，鼠标能动，背景是蓝色的沙漠壁纸，看起来还挺像回事。我正准备收工走人，发现——<strong>没声音</strong>。</p>'
html += '<h2 style="font-size:17px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px 0;padding-left:12px;border-left:4px solid #333;">第一个坑：声卡驱动</h2>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">客户说：「放个音乐试试。」我打开浏览器，搜了一首歌，播放器转圈，没声。设备管理器里一看，显示 "Intel(R) Display Audio"，驱动也在。aplay -l 能识别声卡，alsamixer 看了一圈也没静音。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">折腾了半小时，突然想到——BIOS。进 BIOS 一看，右下角有个 "Onboard Audio: Disabled"。改成 Enabled，保存重启，声音来了。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px"><strong>教训：装系统之前，先进 BIOS 看一遍。尤其是品牌机，不知道之前谁动过什么设置。</strong></p>'
html += '<h2 style="font-size:17px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px 0;padding-left:12px;border-left:4px solid #333;">第二个坑：搜狗输入法乱码</h2>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">客户又说：「微信发个消息试试。」打开微信，登录，打字。打出来的全是方块。搜了一圈，发现麒麟 V10 默认不装 fonts-wqy-microhei。装完重启搜狗——汉字出来了。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px"><strong>教训：装完系统第一件事，先装中文字体。</strong></p>'
html += '<h2 style="font-size:17px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px 0;padding-left:12px;border-left:4px solid #333;">第三个坑：合盖不休眠</h2>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">合上盖子，等了三秒，打开——黑屏。按电源键，没反应。长按电源键强制关机，重新开机，正常。合盖，黑屏。查了 /etc/systemd/logind.conf，发现麒麟默认合盖行为是 HandleLidSwitch=ignore。改成 HandleLidSwitch=suspend——合盖，休眠。开屏，恢复。</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px"><strong>教训：如果是笔记本电脑装麒麟，第一件事就改 logind.conf。</strong></p>'
html += '<h2 style="font-size:17px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px 0;padding-left:12px;border-left:4px solid #333;">后来</h2>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">后来我学聪明了，每次装麒麟之前，先列一个「必改清单」：</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">· BIOS 检查（声卡、硬盘模式、启动模式）</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">· 中文字体包</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">· 合盖行为</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">· 时区改成 Asia/Shanghai</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">· 常用软件：WPS、微信、搜狗、麒麟应用商店</p>'
html += '<p style="font-size:14px;line-height:1.9;color:#333;margin-bottom:15px">拿着这个清单，现在装一台麒麟 V10 从开机到收工，不到一个小时。</p>'
html += '<div style="border-top:1px solid #e0e0e0;margin:30px 0 10px 0;padding-top:20px">'
html += '<p style="font-size:13px;line-height:1.8;color:#666;margin-bottom:5px"><strong>关注我</strong>，下一篇写那次打印机罢工的事——整个楼层，同一时间，一台都打不了。</p>'
html += '<p style="font-size:13px;line-height:1.8;color:#888;margin-bottom:5px;text-align:right">—— 三页札记</p>'
html += '<p style="font-size:13px;line-height:1.8;color:#888;margin-top:10px">每天分享信创运维实战经验。</p>'
html += '</div></section>'

draft_data = {'articles': [{
    'title': '装完麒麟 V10 我踩了三个没人告诉你的坑',
    'author': '三页札记',
    'digest': '那天下午两点，客户把电脑搬到了会议室。',
    'content': html,
    'thumb_media_id': new_id,
    'need_open_comment': 0,
    'only_fans_can_comment': 0
}]}
draft_url = 'https://api.weixin.qq.com/cgi-bin/draft/add?access_token=*** + token
req = urllib.request.Request(draft_url, data=json.dumps(draft_data, ensure_ascii=False).encode(), headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req, timeout=30)
draft = json.loads(resp.read())
print('Draft OK: ' + draft.get('media_id', ''))
print('Done!')
