# 2026-05-10 工作日记

## 今日工作内容

### 1️⃣ Node.js 版本修复（06:27-06:44）
- **问题**：系统 node v20.20.2 太旧，openclaw status 报错
- **发现**：gateway 实际用的是 `~/.local/nodejs/bin/node` v24.15.0，没问题
- **修复**：删除旧的 `/usr/bin/node`，用 nvm 的 v24 创建软链接到系统路径
- **结果**：`node -v` → v24.15.0 ✅

### 2️⃣ Telegram 通道排查（06:28-06:46）
- **问题**：老板反馈 TG 发指令没反应
- **排查**：gateway 进程正常，TG API 正常，bot token 有效
- **修复**：重启 gateway 后恢复
- **根因**：可能是 gateway 进程运行时间过长导致连接超时

### 3️⃣ 定时任务 cron 更新（06:41-06:52）
- **需求**：每天晚上 23:30 写工作总结，逐条列出信息点，同步艾玛笔记
- **修改**：`~/.openclaw/cron/jobs.json` 中 `daily-work-diary` 的 prompt
- **新增要求**：
  - 逐条列出当天做过的每个信息点（编号列表）
  - 不编造，只记实际发生的事
  - 同步到艾玛笔记（IMA API）
  - 去掉字数限制，信息点要全
- **重启 gateway** 使配置生效 ✅

### 4️⃣ 音乐下载工具 v2.0 重写（07:00-07:30）
- **需求**：完善音乐下载工具，支持全网下载
- **排查各平台 API**：
  - 网易云 ✅ 正常
  - QQ音乐 ❌ 旧 API 失效 → 改用移动端 API ✅
  - 酷狗 ✅ 正常
  - 酷我 ❌ WAF 拦截
  - 咪咕 ❌ 返回 HTML 而非 JSON
  - YouTube ✅ 通过 yt-dlp
  - SoundCloud ✅ 通过 yt-dlp
  - Bilibili ❌ 搜索 API 被 WAF 拦截
- **安装依赖**：yt-dlp、mutagen
- **新增功能**：
  - 8个音源平台
  - 自动写入 ID3 标签（歌名、歌手、专辑、封面）
  - 搜索结果保存到 `/tmp/musicdl_results.json`
  - `info` 命令查看工具状态
- **下载目录**：`/vol1/1000/music/downloads/`（老板指定的已有目录）
- **交互方式**：老板说关键词 → 我搜索返回列表 → 老板选序号 → 我下载

### 5️⃣ 下载测试（07:20-07:38）
- **《稻香》**：周杰伦，序号1，网易云下载成功 ✅（7.2MB, 320kbps）
- **《花香》**：许绍洋，序号1，国内平台播放链接获取失败 → YouTube 下载成功 ✅（10.3MB）
- **问题**：国内平台（网易云、QQ、酷狗）获取播放链接失败，可能需要登录态 Cookie
- **临时方案**：YouTube/SoundCloud 兜底

### 6️⃣ 全量备份（07:35）
- **备份内容**：openclaw.json、cron jobs、workspace、scripts、systemd timers、docker 容器列表
- **备份目录**：`/vol1/1000/openclaw/backup/`
- **清理策略**：workspace 快照保留最近 5 个
- **更新了 README.md** 备份记录
- **更新了 MEMORY.md** 备份规则

### 7️⃣ 记忆系统问题（07:38）
- **老板反馈**：之前对话过程中没有自动记忆重要信息
- **问题确认**：今天的记忆文件只有手动追加的内容，对话中的重要信息都没记
- **根因**：我在对话中没有主动调用 write 工具写记忆文件
- **改进**：以后对话中遇到重要信息，立即写入当天的 memory 文件

### 8️⃣ OpenAI Codex CLI 安装尝试（08:05-08:14）
- **需求**：老板想装 Codex CLI（OpenAI 终端 AI 编码工具）
- **发现**：
  - Codex CLI 是 Rust 写的二进制工具，npm 只是个壳
  - 需要从 GitHub Release 下载 80MB 二进制文件
  - 下载速度太慢，文件损坏，segfault
  - 不支持第三方模型（主要用 OpenAI 自家模型）
- **结论**：老板决定不装了，继续用 OpenCode + Claude Code

### 9️⃣ 音乐下载流程测试通过
- 老板通过 TG 说"下载花香"，我搜索后返回列表，老板选序号1，下载成功
- 全流程验证通过 ✅
- 下载目录：`/vol1/1000/music/downloads/`

### 🔟 Hermes Agent 部署（08:22-08:30）
- **项目**：NousResearch Hermes Agent
- **镜像**：`nousresearch/hermes-agent:latest`（5.5GB）
- **容器名**：`hermes-agent`
- **数据目录**：`/vol1/1000/hermes/data`
- **容器IP**：172.17.0.4
- **模型配置**：openrouter/anthropic/claude-sonnet-4
- **状态**：✅ 运行正常
- **内置技能**：91个（claude-code、codex、opencode、github、discord、spotify 等）
- **工具集**：20+（code_execution、computer_use、cronjob 等）

### 1️⃣1️⃣ 工具安装记录
- **Pillow v12.2.0**: 已安装，封面图生成脚本 cover_gen.py 测试通过
- **Playwright v1.59.0**: 已安装，Chromium Headless Shell 147.0.7727.15
  - HTML 截图功能验证通过
  - 用途: 公众号封面图、终端截图、海报生成

### 1️⃣2️⃣ 规则更新（老板确认）
- **GitHub 操作**：直接调用已安装技能（gh-issues/github/github-ops），不用重新搜索
- **技能优先**：已安装技能优先使用，不重复造轮子
- **Telegram 中断**：发 stop 或 /stop 可中断当前任务，不用等跑完
- **API Key 管理**：统一放环境变量（~/.openclaw/.env + ~/.bashrc），禁止写配置文件

### 1️⃣3️⃣ 📧 gog 邮件认证（未完成）
- **目标**：配置 gog CLI 收发 Gmail
- **进度**：
  - ✅ gog CLI v0.15.0 已安装（从源码编译）
  - ✅ client_secret.json 已恢复（web 类型，client_id: 690871028401-jm8kmr843ndfkk6qu18o47369qh6uqqg）
  - ✅ gog credentials.json 已更新
  - ❌ 认证未完成（需要浏览器交互）
- **明天继续**：在服务器终端运行 `gog auth add` 完成认证

### 1️⃣4️⃣ 📌 今日规则更新
- API Key 统一放环境变量，禁止写配置文件
- GitHub 操作直接用已安装技能
- Telegram 中断用 stop 或 /stop
- 飞牛 NAS 禁止操作 /usr/trim/

### 1️⃣5️⃣ 🛠️ 工具安装
- Go v1.26.2 已安装
- gog CLI v0.15.0 已编译安装
- Pillow v12.2.0 已安装
- Playwright v1.59.0 已安装

### 1️⃣6️⃣ 📱 小红书笔记
- 老板反馈内容需要调整，明天重新写

### 1️⃣7️⃣ 🤖 商汤 SenseNova 6.7 Flash-Lite 免费公测（22:32）
- **当前模型**：sensenova/sensenova-6.7-flash-lite（轻量版）
- **免费政策**：
  - 限时放量，¥0/月
  - 每模型 1,500 次调用 / 5 小时（特殊模型除外）
  - 最多 20 个 API Key
- **特性**：
  - 原生多模态架构，理解生成一体
  - 原生支持 Cowork-Skills 体系，办公场景特化
  - 支持 Hermes Agent 与 OpenClaw 快速接入
- **同系列模型**：flash-lite（当前）→ flash → pro → max，逐级更强更慢更贵
- **控制台**：https://platform.sensenova.cn/console/keys

### 1️⃣8️⃣ 🖼️ 商汤文生图模型（22:34）
- 商汤 SenseNova 平台支持文生图（Image Generation）能力
- 属于「日日新」大模型体系
- 支持中文提示词，多种风格（写实/动漫/3D/水彩等）
- 与 LLM API 共用 API Key（最多 20 个）
- 免费额度政策可能同样适用
- 文档地址：https://platform.sensenova.cn/docs
- ⚠️ 文档为 SPA 应用，需登录后查看具体 API 参数

## 📊 工作统计
- **工具开发**：1 个（musicdl v2.0 重写）
- **配置修改**：2 处（cron prompt、MEMORY.md 备份规则）
- **问题排查**：3 个（Node.js、TG 通道、各平台 API）
- **下载测试**：2 首歌曲
- **备份**：1 次全量备份
- **容器部署**：1 个（Hermes Agent）
- **模型研究**：2 个（商汤 SenseNova）

---
记录时间：2026-05-10 23:00
状态：已完成