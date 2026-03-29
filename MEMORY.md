# MEMORY.md — 贾维斯的长期记忆 🤖

## 关于老板

- **名称：** Young，喜欢被叫"老板"
- **技术背景：** 运维工程师，熟悉 Linux、飞牛NAS、信创系统（麒麟/UOS）、nginx、docker、mihomo 代理
- **飞牛NAS：** 系统自带防火墙，安全审计不要检查 iptables/ufw（会误报）
- **沟通风格：** 直接、不废话、偏好技术交流
- **工作内容：** 信创电脑运维、多通道 AI 助手搭建

## 账号信息

- **Telegram：** @XNM_SHR (ID: 460212872)
- **飞书 open_id：** ou_3c1068d79dee7c0e06ffb89eb461aed7
- **NAS 服务器：** threelnas (192.168.31.58)，Linux

## 飞书群组

- **牛马公司** (oc_34f560ad2af0a629b9ef9ae189ba7a63)
  - 群主：老板 (ou_3c1068d79dee7c0e06ffb89eb461aed7)
  - 机器人：贾维斯（我，open_id: ou_54dd61b5665602b33d114a74de31fb8d）、柠檬 (ou_0fa64f2f61b81b8b9ad200b5d059d4fa, App: cli_a91b005a9db89ccd)、喵喵 (ou_351a85030be5f6d5fca2de0a3d5998e6, App: cli_a9140c5134b99cd5)
  - ⚠️ 飞书机器人之间 @ 不会触发响应（平台限制）
  - 发消息给其他机器人时，用老板个人身份发送，不用机器人身份
- **记笔记规则**：老板让我记笔记时，同时同步一份到飞书知识库

## 模型配置

- **主模型：** openrouter/xiaomi/mimo-v2-pro（小米免费体验中）
- **备用：** openrouter/xiaomi/mimo-v2-pro、openrouter/nvidia/nemotron-3-super-120b-a12b:free、stepfun/step-3.5-flash:free
- **新增：** openrouter/qwen/qwen3-coder:free（别名 Qwen3-Coder）、openrouter/openai/gpt-oss-120b:free（别名 GPT-OSS）
- **其他：** zai/glm-4-flash（免费，别名 GLM-Flash）、moonshot/kimi-k2.5（直连，别名 Kimi）
- **代理：** Mihomo 127.0.0.1:7890（Telegram API 需要代理）
- ⚠️ **切换规则：** 小米 MiMo 免费体验结束后，自动切换到千问3（qwen/qwen3-next-80b-a3b-instruct:free）

## 已安装的技能

- **github** — gh CLI 操作
- **ima-skill** — 艾玛笔记/知识库管理（已配置凭证）
- **wechat-mp-writer** — 微信公众号文章写作
- **wechat-mp-publisher** — 微信公众号发布（手动安装，源码在 skills/ 目录）

## 老板的暗号

- **小龙虾** = OpenClaw

- **AppID：** wx97bc84bb54232e27
- **IP 白名单：** 111.19.33.189（可能变动，推送前需检测）
- **作者：** 三页札记
- **推文规则：** 每篇必须标记原创

## 公众号推文优化规则（2026-03-26 更新）

### 配图规范
- **封面**：简洁大气，少文字，吸引点击（白底+图标+标题，不要堆砌内容）
- **文中配图**：终端截图风格（用 HTML+Playwright 截图，不用 cairo/PIL）
- **图片生成工具**：`wechat-image-generator` + Playwright 浏览器截图

### 代码块规范
- 使用 `<pre>` 标签（不用 `<div>` 或 `<table>`，微信不支持）
- 背景色 `#0d1117`，文字色 `#e6edf3`，圆角 `border-radius:8px`
- 语法高亮：关键字 `#ff7b72`（红）、路径 `#a5d6ff`（蓝）、输出 `#7ee787`（绿）
- 边框 `border:1px solid #30363d`
- 横向滚动 `overflow-x:auto`

### 发布流程
1. HTML 模板 → Playwright 截图 → 生成配图
2. 上传封面+正文图片到微信素材库
3. 构建 HTML 正文（`<pre>` 标签 + 内联样式）
4. 创建草稿到公众号

### 踩坑记录
- `div` 的 `background` 样式会被微信过滤掉
- `table` 的 `border-radius` 不生效
- `<pre>` 标签是最稳定的代码块方案
- PIL/cairo 中文渲染有问题，用 HTML+Playwright 截图

## 艾玛笔记

- **doc_id（OpenClaw 更新摘要）：** 7442338850827660
- **doc_id（2026-03-27 工作笔记）：** 7443339976640110
- **doc_id（2026-03-28 工作日记）：** 7443685675395433

## 飞书日记

- **doc_id（贾维斯工作日记）：** QBN9d0mi5oVEd1xEuB2c1nuhnCg
- **链接：** https://www.feishu.cn/docx/QBN9d0mi5oVEd1xEuB2c1nuhnCg
- **用途：** 每天追加当天的工作日记

## 运维规则

1. Gateway 重启成功后，通过微信通道发通知"Gateway 重启成功 🍋"（**必须执行，这是硬规则**）
   - 实现方式：systemd timer 每 15 秒检测 Gateway 启动时间变化，自动调用 `openclaw message send` 发通知
   - 脚本：`~/.openclaw/check-restart-notify.sh`
   - Timer：`~/.config/systemd/user/openclaw-restart-notify.timer`
   - 不消耗 token，纯 bash + systemd
2. 微信公众号推送前检测 IP，变了通知老板更新白名单
3. 修改/更新前先让老板确认
4. 每天 8:00 安全审计定时任务，结果推微信
5. NAS 监控：每 5 分钟检查 IPv6 变动、CPU/内存/磁盘告警，推微信（零 token 消耗）

## 定时任务

- **daily-security-audit** — 每天 8:00，安全审计，结果推微信
- **daily-weather** — 每天 6:00，西安两地天气播报，推微信
- **weather-alert** — 每 3 小时（6:00-22:00），异常天气告警，推微信

## 公众号推文写作流程（标准7步）

**1. 确认选题和类型**
→ 老板说主题，判断是"实战教程/踩坑经验/工具推荐/新闻资讯"哪类

**2. 写初稿**
→ drafts/ 目录下生成 markdown，结构和技术内容先确定

**3. 去 AI 味润色**
→ 口语化、加具体场景、去掉套话排比、保持技术准确性（不改事实，只改文风）

**4. 生成配图**
→ 终端截图：HTML 终端模板 → Playwright `el.screenshot()` 截元素（不带黑边框）
→ 封面图：HTML 模板 → 2400×1350 高清截图

**5. 上传素材**
→ 先检测 IP 白名单（check_wechat_ip.sh）
→ 图片上传到微信素材库（永久素材 /cgi-bin/material/add_material?type=image）
→ 封面单独上传 thumb 类型

**6. 构建 HTML**
→ 代码块用深色 `<pre>` 样式（可复制）
→ 按文章类型排版
→ 末尾加关注引导 + 往期推荐（不加链接，微信拦截外部 URL）

**7. 推送草稿**
→ 调用微信 draft/add API
→ 老板在公众号后台确认发布

## 公众号排版规范（核心规则，所有文章通用）

- 封面图：2400×1350 高清（永久素材上传），用 `el.screenshot()` 截元素
- 代码块：`<pre style="background:#1e1e1e;color:#d4d4d4;padding:14px 18px;border-radius:8px;font-family:Menlo,Consolas,monospace;font-size:14px;line-height:1.6;overflow-x:auto;margin:10px 0">`（用户长按可复制）
- 终端截图：用 `el.screenshot()` 截元素，不要整页截（避免黑色边框），`device_scale_factor=2` 保证高清
- 文章末尾：关注引导卡片 + 往期推荐（不加链接，微信 API 拦截外部 URL）

## 去 AI 味规则（2026-03-29 总结）

- **开头**：用具体场景代替套话（"上周同事找我" > "做运维久了最怕听到"）
- **标题**：口语化（"往下挖，看谁吃的最多" > "第二步：一级子目录排查"）
- **语气**：去掉排比、对仗、八股文风（"就一个思路" > "三板斧"）
- **套话黑名单**：对症下药、运维效率翻倍、三板斧、不废话、干货满满
- **底线**：内容和事实绝对不改，只改表达方式
- **目标**：读起来像一个真人在聊天，不是机器人在写模板

## 公众号文章类型模板（根据内容灵活选择）

### 1. 实战教程类（步骤操作、命令行教学）
- 标题用 `<h3>`，列表用 `<p>` 不用 `<ul><li>`
- 代码块用深色 `<pre>` 样式
- 每步配终端截图（`el.screenshot()` 截终端元素）
- 结尾加"避坑提醒"和"总结"
- 例：磁盘清理技巧、软件源配置

### 2. 踩坑经验类（问题→排查→解决）
- 开头抛出真实场景
- 按"问题→原因→解决"结构展开
- 代码块 + 检查清单
- 例：打印机共享踩坑、系统升级翻车

### 3. 工具推荐/速查类
- 简洁为主，少截图，多代码块
- 可用表格对比
- 例：常用命令速查、运维工具箱

### 4. 新闻资讯/观点类
- 纯图文，不需要代码块
- 配图用高清图片
- 例：信创政策解读、行业动态

## 飞书 MCP

- 已安装 @larksuiteoapi/lark-mcp，通过 mcporter 调用
- 支持文档创建/导入（用 tenant token，不需要 OAuth）
- 飞书应用权限已开通：docs:doc, docx:document, drive:drive, wiki:wiki

## 重要事件

- **2026-03-24：** 初始搭建，配置了 Telegram/飞书/微信三个通道，IMA 知识库，公众号 API，安全审计系统
- **2026-03-25：** 修复 gateway 入口文件、安装 GitHub 技能、整理 OpenClaw 版本更新内容、飞书群机器人交互探索、创建群头像、每日安全审计定时任务、公众号文章排版发布、替换 OpenRouter API Key、恢复 Telegram 命令菜单
- **2026-03-28：** 安全审计修复 + nginx 反代 + Home Assistant 部署 + 小米 181 设备接入 + 智能家居监控 + 科技新闻系统 + Google Workspace OAuth 授权 + gog CLI + memory-lancedb-pro 安装

## 待办

- [ ] 公众号推文原创标记需手动勾选（API 不支持）
- [ ] Google token refresh token 配置（access token 1 小时过期，需自动续期）
- [ ] memory-lancedb-pro 提取参数优化（噪音太多）
- [ ] 红米 AX5 路由器 HA 集成（暂无插件）
- [ ] Twitter API Token

## 图片生成技能

- **wechat-image-generator** — 用 HTML 模板 + Playwright 浏览器截图生成图片
- **路径：** `~/.openclaw/workspace/skills/wechat-image-generator/`
- **用法：**
  1. `python3 scripts/generate.py cover --title "标题" --subtitle "副标题" --output /tmp/xxx.html`
  2. 确保本地 HTTP 服务器运行：`python3 -m http.server 18888 --directory /tmp &`
  3. `playwright screenshot --viewport-size=1200,675 http://127.0.0.1:18888/xxx.html /tmp/xxx.png`
- **优势：** 浏览器渲染中文完美，零 token 消耗
- **依赖：** Playwright Chromium（已安装）、本地 HTTP 服务器
- **注意：** OpenClaw 的 browser 工具不支持 file:// 协议，必须走 HTTP
- **样式：** 支持深色科技风、简约白、霓虹暗黑、暖色渐变等多种配色
- **终端截图技巧：** 用 `el.screenshot()` 截终端元素，不要整页截（避免黑色边框），device_scale_factor=2 保证高清

## 智能家居（2026-03-28 新增）

### Home Assistant 部署
- **地址**：https://ai.threel.site（SSL，飞牛证书）
- **Docker 容器**：homeassistant（ghcr.io/home-assistant/home-assistant:stable）
- **配置目录**：/vol1/1000/docker/homeassistant/config/
- **已装插件**：HACS、Xiaomi Miot Auto（小米设备集成）

### 小米设备（共 181 个实体）
- 照明：吸顶灯 ×4（客厅/大卧室/小卧室/阳台）、台灯
- 影音：小米电视、小米盒子、小爱音箱 mini、Mi Smart Clock 4寸
- 家电：空调（1.5匹）、热水器（云米）、冰箱（云米 456L）、电磁炉、电饭煲、微波炉、空气炸锅、破壁机
- 安防：小米 360° 摄像机 2K、摄像机2、米家摄像机
- 插座：智能插座 Mini、米家智能插座增强版、空调插座
- 传感器：温湿度计、体脂秤、手环 9 Pro
- 网络：小米路由器（红米 AX5，未集成）

### 定时任务
- **smart-home-monitor**：每 3 分钟检查设备变化，有告警推微信
  - 监控：摄像头移动侦测、空调温度、热水器、插座功耗、温湿度异常
  - 脚本：~/.openclaw/workspace/scripts/smart_home_monitor.sh

### Nginx 反代（新增）
- `nas.threel.site` → :5666（飞牛 NAS）
- `cloud.threel.site` → :5244（云盘）
- `ai.threel.site` → :8123（Home Assistant）
- 证书：飞牛 NAS 自动生成的 SSL 证书

### 注意事项
- 小米账号开了双重认证，Xiaomi Miot 登录时需临时关 2FA
- 路由器（红米 AX5）没有 HA 插件支持
- 很多设备显示 unavailable 是因为不在同一网段或休眠

### 在家判断逻辑
- 老板手机 IP：192.168.31.220
- 判断方式：ping 手机，通 = 在家，不通 = 不在家
- 规则：在家不推摄像头告警，不在家才推
- 其他设备变化（空调/热水器/插座）不管在不在家都推

## Google Workspace (2026-03-28)
- **账号：** aqiyoung.lee@gmail.com
- **已授权 scope：** Gmail + Calendar
- **Token 文件：** ~/.openclaw/workspace/google_token.json
- **gog CLI：** v0.12.0，需代理（`export https_proxy=http://127.0.0.1:7890`）
- **用法：** `gog --access-token "$TOKEN" gmail search "in:inbox"`
- ⚠️ access token 1 小时过期，需后续配置 refresh token 自动续期
- 飞书日历也可用：`feishu_calendar_calendar` / `feishu_calendar_event` 工具

## 飞书规则补充 (2026-03-28)
- 飞书全员消息发到「牛马公司」群 (oc_34f560ad2af0a629b9ef9ae189ba7a63)
- 不再发到客户对话群

## memory-lancedb-pro (2026-03-28)
- memory-lancedb-pro v1.1.0-beta.9 已安装
- 安装路径：/home/liyang/node_modules/memory-lancedb-pro
- Embedding：SiliconFlow BGE-large-zh-v1.5（免费中文模型）
- SiliconFlow API Key：sk-kgsuhpdtuiwbyfjfsdvlkyffbfubvlbapkdnulvbobpoftmp
- 配置在 openclaw.json 的 plugins.entries.memory-lancedb-pro
- 功能：自动提取对话记忆，向量检索，自动回忆

## 已安装的定时任务
- daily-tech-news：每天 8:00 推送科技/AI新闻聚合
- smart-home-monitor：每 3 分钟检查智能家居设备变化
- daily-weather：每天 6:00 推送天气
- weather-alert：每 3 小时检查异常天气
- daily-security-audit：每天 8:00 安全审计
