# MEMORY.md — 小七的长期记忆 🤖

> 上次梦境更新：2026-05-13。目标：保持在 200 行以内，索引而非堆砌。

## 关于老板

- **名称：** Young，喜欢被叫"阳仔"
- **技术背景：** 运维工程师，熟悉 Linux、飞牛NAS、信创系统（麒麟/UOS）、nginx、docker、mihomo 代理
- **飞牛NAS：** 系统自带防火墙 + 二次登录验证（2FA），安全审计不要检查 iptables/ufw 和 fail2ban（会误报）
- **⚠️ 禁令：绝对不允许操作飞牛 NAS（trim 系统）的 `/usr/trim/` 下任何文件！之前修改 nginx 配置导致系统崩溃。修改飞牛任何配置前必须先备份并让老板确认。**
- **备份规则：所有备份统一放到 `/vol1/1000/openclaw/backup/` 目录下，子目录按项目划分**
- **每次备份后必须在 `/vol1/1000/openclaw/backup/README.md` 中记录一条备份信息**
- **⚠️ 备份铁律：每次重要变更后必须立即备份！包括：改配置、装新工具、改脚本、改定时任务等。**
- **沟通风格：** 直接、不废话、偏好技术交流
- **工作内容：** 信创电脑运维、多通道 AI 助手搭建

## 账号信息

- **Telegram：** @XNM_SHR (ID: 460212872)
- **OpenList 管理员：** admin / @Young2026!（https://cloud.threel.site）
- **飞书 open_id：** ou_3c1068d79dee7c0e06ffb89eb461aed7
- **NAS 服务器：** threelnas (192.168.31.58)，Linux
- **GitHub：** 已配置 gh CLI + token

## 飞书群组

- **牛马公司** (oc_34f560ad2af0a629b9ef9ae189ba7a63)
  - 群主：老板
  - 机器人：小七（我）、柠檬、喵喵
  - ⚠️ 飞书机器人之间 @ 不会触发响应（平台限制）

## 模型配置

- **主模型：** longcat/LongCat-2.0-Preview
- **Provider：** OpenRouter、NVIDIA NIM、小米 Token Plan、LongCat、SenseNova、ZAI
- **代理：** Mihomo 127.0.0.1:7890（Telegram API 需要代理）

## 已安装的技能

- **github / gh-issues / github-ops** — GitHub 操作
- **ima-skill** — 艾玛笔记/知识库管理
- **wechat-mp-writer / wechat-mp-publisher** — 微信公众号写作与发布
- **huashu-design** — 设计生成（原型、幻灯片、动画）
- **agent-dream** — 梦境系统（记忆整合与自我反思）
- **openclaw-spirits** — 灵兽系统
- **summarize** — 网页总结
- **weather** — 天气查询
- **pptx-generator** — PPT 生成
- **minimax-docx / minimax-pdf / minimax-xlsx** — 文档处理
- **feishu-bitable / feishu-calendar / feishu-task** — 飞书系列
- **music-download** — 音乐下载
- **gog / google-workspace** — Google Workspace（Gmail/日历/Drive）
- **self-improving** — 自我改进
- **proactive-agent-lite** — 主动代理

## 老板的暗号

- **小龙虾** = OpenClaw

## 微信公众号

- **AppID：** wx97bc84bb54232e27
- **AppSecret：** ***
- **IP 白名单：** 111.19.39.227（可能变动，推送前需检测）
- **作者：** 三页札记
- **推文规则：** 每篇必须标记原创
- **⚠️ 公众号 API 走代理，白名单填代理出口 IP，不是服务器 IP**
- **⚠️ 每次推送前必须先检测 IP，变了则通知老板更新白名单**

### 公众号推文规范

- **封面图**：2400×1350，用 `scripts/cover_gen.py`（PIL + 思源黑体）
- **代码块**：`<pre>` 内联样式，body 不设 max-width
- **版本管理**：每次生成内容保存到 `drafts/` 目录，文件命名 `文章标题_v版本号.md`
- **发布流程**：写稿 → 去AI味 → 配图 → 上传素材 → 构建HTML → 推草稿

### 内容限制

- **绝对不能涉及**：VPN、翻墙、代理工具（mihomo/Clash/V2Ray 等）、Telegram
- **可写内容**：信创运维、Linux 技巧、Docker、nginx、系统监控、AI 工具、开源项目

## 艾玛笔记（IMA）— 操作规则

> **重要：这个规则所有模型都必须遵守！**

### 用途
- 每天新建一篇工作日记
- 标题格式：`YYYY-MM-DD 周X — 小七工作日记`

### 凭证位置
```
~/.config/ima/client_id
~/.config/ima/api_key
```

### 写入笔记（新建）
**必须使用 `import_doc` 接口**

```bash
curl -s -X POST "https://ima.qq.com/openapi/note/v1/import_doc" \
  -H "ima-openapi-clientid: $IMA_CLIENT_ID" \
  -H "ima-openapi-apikey: $IMA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "标题",
    "content_format": 1,
    "content": "Markdown 内容"
  }'
```

**关键参数：**
- `title`：笔记标题
- `content_format`: `1`（Markdown 格式，固定）
- `content`：笔记正文（Markdown 格式）

### ⚠️ 注意事项
1. **content_format 必须是 1**（Markdown 格式），不要改成 0 或 2
2. **不要自己发明 API 写法**，严格按照上面的模板
3. 如果记不住，**先读 `~/.openclaw/workspace/skills/ima-skill/notes/SKILL.md`**
4. 凭证永远在 `~/.config/ima/` 下，不要改位置

## 飞书日记

- **doc_id：** QBN9d0mi5oVEd1xEuB2c1nuhnCg
- **链接：** https://www.feishu.cn/docx/QBN9d0mi5oVEd1xEuB2c1nuhnCg
- **用途：** 按日期追加工作日记

## 运维规则

- **安全审计过滤**：VOL00 是 Windows 数据盘，不参与安全审计的磁盘使用率检测

1. Gateway 重启成功后，通过微信通道发通知"Gateway 重启成功 🍋"（**硬规则**）
   - 实现：systemd timer 每 15 秒检测，脚本 `~/.openclaw/check-restart-notify.sh`
2. 微信公众号推送前检测 IP，变了通知老板更新白名单
3. **修改/更新前先让老板确认，重启 Gateway 也必须先确认**
4. **有风险的命令必须先确认**——重启服务、改配置、删除文件、对外操作等
5. **能本地化的定时任务尽量本地化**（systemd timer + bash），减少 token 消耗

## 定时任务

### OpenClaw cron（消耗 token）
- **daily-work-diary** — 每天 23:30，整理工作日记，同步艾玛笔记 + 飞书日记
- **daily-security-audit** — 每天 8:00，安全审计，结果推 Telegram
- **daily-weather** — 每天 6:00，西安天气播报，推 Telegram
- **daily-ai-skills-search** — 每天 10:00，AI 技能搜索
- **agent-dream** — 每天 3:00 AM，记忆整合与自我反思

### systemd timers（零 token，本地化）
- **openclaw-restart-notify** — 每 15 秒，Gateway 重启通知

## 重要事件时间线

- **2026-03-24** — 初始搭建，配置 Telegram/飞书/微信三个通道
- **2026-05-08** — 系统重装后恢复（nginx 反代、FNMessageBots Telegram 推送、定时任务）
- **2026-05-11** — 信创推文写作发布 + web_search 修复（ddg → duckduckgo）

## 踩坑记录（精华版）

### 微信相关
- `<pre>` 标签是最稳定的代码块方案
- body 不设 max-width，代码块用 pre 内联样式
- 长 content 会触发微信 WAF 拦截（501）

### 系统相关
- 飞牛 NAS `/usr/trim/` 下文件绝对不能动（导致过系统崩溃）
- web_search provider 正确名是 `duckduckgo`（不是 `ddg`）
- 国内平台音乐下载需要登录态 Cookie

## 安全规则

- **API Key 管理**：所有 API Key 统一放到环境变量（~/.openclaw/.env 和 ~/.bashrc），禁止写入 openclaw.json 等配置文件
- **飞牛 NAS 禁令**：绝对不允许操作 `/usr/trim/` 下任何文件
- **备份铁律**：每次重要变更后必须立即备份

## 音乐下载
- **技能**：`skills/music-download/SKILL.md`
- **下载目录**：`/vol1/1000/music/downloads/`
- **搜索**：`python3 musicdl.py search "关键词"`（只输出歌名+时长+平台）
- **下载**：`yt-dlp "ytsearch1:歌手 歌名" -x --audio-format mp3 -o "/vol1/1000/music/downloads/%(title)s.%(ext)s" --no-playlist`

## 邮件发送
- **发邮件**：`gog gmail send --to xxx --subject xxx --body xxx --attach xxx`
- **老板 QQ 邮箱**：278948670@qq.com
- **发件账号**：aqiyoung.lee@gmail.com（通过 gog CLI 发送）

## 备份规则

- **备份目录**：`/vol1/1000/openclaw/backup/`
- **workspace 快照**：`workspace-snapshot-YYYYMMDD/`（保留最近 5 个）
- **配置备份**：`openclaw.json.bak.YYYYMMDD_HHMMSS`（保留最近 3 个）
- **备份铁律**：每次重要变更后必须立即备份

## 工具路径速查

- 封面图生成：`scripts/cover_gen.py`（PIL，思源黑体）
- 终端截图：`skills/wechat-image-generator/`（Playwright）
- 音乐下载：`scripts/musicdl.py`
- Gateway 重启通知：`~/.openclaw/check-restart-notify.sh`
- 备份目录：`/vol1/1000/openclaw/backup/`
- 公众号草稿：`drafts/`
- 下载目录：`/vol1/1000/music/downloads/`

## FNMessageBots（飞牛 NAS 事件推送）

- **位置**：`/vol1/1000/FNMessageBots/`
- **容器**：`fn-message-bot`
- **Telegram Bot**：`@xiaozht_bot`（飞牛日志），Chat ID：460212872
- **功能**：监控 NAS 事件（登录、SSH、CPU、内存、磁盘等）→ 推送到 Telegram
- **⚠️ 容器重启需老板在 NAS 终端执行**：`docker restart fn-message-bot`

## Cloudflare

- **API Token**：已保存到 `~/.openclaw/.env`（CF_API_TOKEN）
- **Account ID**：`1caaacb82c8c6a0d441ef9a803f2e640`

## 梦境系统

- **技能**：`skills/agent-dream/SKILL.md`
- **定时任务**：每天凌晨 3:00
- **功能**：记忆整合、自我反思、长期记忆维护
- **梦境目录**：`memory/dreams/`

## GitHub 项目处理规则

- **用户发送 GitHub 链接时**：必须用 `gh` CLI 读取，禁止用 web_fetch/web_search
- **videodl** — 轻量级视频下载器，支持50+平台，License：PolyForm Noncommercial 1.0.0（禁止商用）