# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking infrastructure.

---

## 飞书消息规则

- 微信通道要求发飞书消息 → 发到老板的飞书个人号（ou_3c1068d79dee7c0e06ffb89eb461aed7）
- 使用飞书 tenant_access_token + im/v1/messages API 直接发送

---

## 运维监控

- **Gateway 重启通知**：每次 gateway 重启成功后，必须通过微信通道（openclaw-weixin）给老板发一条"Gateway 重启成功 🤖"的提示消息（**铁律，不能忘**）
  - 自动化方案：systemd timer + bash 脚本，每 15 秒检测启动时间变化
  - 脚本：`~/.openclaw/check-restart-notify.sh`
  - Timer：`~/.config/systemd/user/openclaw-restart-notify.timer`
  - 零 token 消耗，纯系统级监控

- **NAS 监控**：每 5 分钟检查 IPv6 变动、CPU/内存/磁盘告警
  - 脚本：`~/.openclaw/nas-monitor.sh`
  - Timer：`~/.config/systemd/user/nas-monitor.timer`
  - 监控内容：IPv6 地址变动、CPU > 90%、内存 > 85%、磁盘 > 90%
  - 告警恢复也会通知
  - 零 token 消耗

- **NAS 事件推送**：本地 Python 脚本监听数据库，直接推 Telegram
  - 脚本：`scripts/nas_telegram_monitor.py`
  - 服务：`systemctl status nas-telegram-monitor.service`
  - Bot：`@xiaozht_bot`（Chat ID：460212872）
  - 数据库：`/usr/trim/var/eventlogger_service/logger_data.db3`
  - 日志：`/vol1/1000/FNMessageBots/data/cursor/monitor.log`

## 微信公众号推文规则

- **作者**：三页札记
- **原创标记**：每篇推文必须标记为原创
- **IP 白名单**：公网 IP 变动时需通知老板更新微信后台白名单（AppID: wx97bc84bb54232e27）
- **⚠️ 公众号 API 走代理，白名单填代理出口 IP，不是服务器 IP**

---

## 封面图生成

- **首选方案**：AI API 生成（ModelScope Z-Image-Turbo）
  - 脚本：`scripts/imgforge.py`
  - 环境变量：`MODELSCOPE_API_KEY`（需要配置）
  - 免费额度：每天约 1000-2500 张
  - 用法：`python3 scripts/imgforge.py "描述" -o output.png -W 2400 -H 1350`

- **备选方案**：PIL 本地生成
  - 脚本：`scripts/cover_gen.py`
  - 字体：`scripts/noto_sc.otf`（思源黑体）
  - 4种风格：深蓝/深绿/黄黑/白底
  - 用法：`python3 scripts/cover_gen.py 1 "主标题" "副标题" output.png`

- **当前状态**：ModelScope API Key 缺失，需要老板提供

---

## 工具路径速查

| 工具 | 路径 | 用途 |
|------|------|------|
| 封面图生成 | `scripts/cover_gen.py` | PIL + 思源黑体，4种风格 |
| 封面图生成(AI) | `scripts/imgforge.py` | ModelScope API |
| 音乐下载 | `skills/music-download/scripts/musicdl.py` | 多平台搜索+下载 |
| Gateway重启通知 | `~/.openclaw/check-restart-notify.sh` | 每15秒检测 |
| NAS监控 | `~/.openclaw/nas-monitor.sh` | 每5分钟检测 |
| NAS事件推送 | `scripts/nas_telegram_monitor.py` | 数据库监听+Telegram推送 |
| 安全审计 | `scripts/security_audit.sh` | 每天8:00 |
| 备份目录 | `/vol1/1000/openclaw/backup/` | 所有备份统一放这里 |
| 公众号草稿 | `drafts/` | 推文草稿 |
| 音乐下载目录 | `/vol1/1000/music/downloads/` | 音乐下载 |
| 终端截图 | `skills/wechat-image-generator/` | Playwright |

---

## 梦境系统（agent-dream）

- **技能**：`skills/agent-dream/SKILL.md`
- **定时任务**：每天凌晨 3:00
- **功能**：记忆整合、自我反思、长期记忆维护
- **梦境目录**：`memory/dreams/`
- **配置**：`skills/agent-dream/assets/dream-config.json`
- **规则**：不要手动干预梦境运行，让它自动执行

---

## PPT 生成（pptx-generator）

- **技能**：`skills/pptx-generator/SKILL.md`
- **用法**：当用户需要生成 PPT/幻灯片时使用此技能
- **注意**：不要自己手搓 pptxgenjs，用 skill 的标准流程
- **依赖**：pptxgenjs（已安装）

---

## 关键命令速查

### 音乐下载
```bash
# 搜索（只输出序号列表）
cd ~/.openclaw/workspace/skills/music-download/scripts && python3 musicdl.py search "关键词"

# 下载（用户选序号后直接用 yt-dlp）
yt-dlp "ytsearch1:歌手 歌名" -x --audio-format mp3 -o "/vol1/1000/music/downloads/%(title)s.%(ext)s" --no-playlist
```

### 邮件发送
```bash
gog gmail send --to 278948670@qq.com --subject "标题" --body "内容" --attach "文件路径"
```

### 公众号发布
```bash
# 获取 token
curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx97bc84bb54232e27&secret=31dd5e8ce9bf116d1b5ca3b81c2d82ea"

# 上传封面
curl -s "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$TOKEN&type=thumb" -F "media=@cover.png"

# 创建草稿
curl -s "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$TOKEN" -H "Content-Type: application/json" -d @draft.json
```

### 飞书消息
```bash
# 获取 tenant_access_token
curl -s "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" -H "Content-Type: application/json" -d '{"app_id":"xxx","app_secret":"xxx"}'

# 发送消息
curl -s "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" -H "Content-Type: application/json" -d '{"receive_id":"ou_xxx","msg_type":"text","content":"{\"text\":\"消息内容\"}"}'
```

### NAS 事件推送
```bash
# 查看服务状态
systemctl status nas-telegram-monitor.service

# 查看日志
tail -f /vol1/1000/FNMessageBots/data/cursor/monitor.log

# 手动触发测试消息
python3 -c "
import requests
TOKEN = '8697554205:AAEcZTEujwIW-baszmhiqRTXFqbOtP3LRsg'
CHAT_ID = '460212872'
url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
proxies = {'https': 'http://127.0.0.1:7890'}
resp = requests.post(url, json={'chat_id': CHAT_ID, 'text': '测试消息'}, proxies=proxies, timeout=10)
print(resp.status_code, resp.text)
"
```

---

## Cloudflare

- **API Token**：`~/.openclaw/.env`（CF_API_TOKEN）
- **Account ID**：`1caaacb82c8c6a0d441ef9a803f2e640`
- **操作前需绕过代理**：`unset HTTP_PROXY HTTPS_PROXY`

---

## Telegram 推送

- **Bot**：`@xiaozht_bot`，Chat ID：460212872
- **推送方式**：本地 Python 脚本 `nas_telegram_monitor.py`（不走 FNMessageBot 容器）
- **脚本通过代理推送**：`proxies = {'https': 'http://127.0.0.1:7890'}`

---

## GitHub 项目处理

- **用户发送 GitHub 链接时**：必须用 `gh` CLI 读取，禁止用 web_fetch/web_search
- **读取 README**：`gh api repos/{owner}/{repo}/contents/README.md --jq '.content' | base64 -d`
- **获取项目信息**：`gh api repos/{owner}/{repo} --jq '.description, .stargazers_count, .language'`
- **搜索项目**：`gh search repos "关键词" --limit 10`
- **Clone 项目**：`gh repo clone {owner}/{repo}`

---

## 网络检测工具

- **脚本**: `scripts/network_check.sh`
- **功能**: IP查询（直连/代理）、连通性测试、mihomo状态、DNS泄露检测、网站分流测试
- **用法**: `bash scripts/network_check.sh`
- **输出**: 彩色的终端报告，包含出口IP、Ping、HTTPS连通性、mihomo节点状态、DNS泄露、网站访问速度
- **依赖**: curl, python3, dig（可选）

---

## 模型切换

- **命令**：通过 Telegram 发送 `/model` 相关命令
- **功能**：查看状态、切换模型、测试连通性、重载配置
- **配置文件**：`~/.openclaw/openclaw.json`
- **热重载**：`kill -SIGUSR1 to gateway process`
