# MEMORY.md — 小七的长期记忆 🤖

> 上次梦境更新：2026-06-10。目标：保持在 200 行以内，索引而非堆砌。

## 关于threely

- **名称：** Young，喜欢被叫"阳仔"
- **技术背景：** 运维工程师，熟悉 Linux、飞牛NAS、信创系统、nginx、docker、mihomo 代理
- **沟通风格：** 直接、不废话、偏好技术交流
- **暗号：** 小龙虾 = OpenClaw

## 账号信息

- **Telegram：** @XNM_SHR (ID: 460212872)
- **飞书 open_id：** ou_3c1068d79dee7c0e06ffb89eb461aed7
- **NAS 服务器：** threelnas (192.168.31.58)
- **飞书群组：** 牛马公司 (oc_34f560ad2af0a629b9ef9ae189ba7a63)

## 模型配置

- **主模型：** `tokenrouter/MiniMax-M3`（0G Router，2026-06-17 切换，1M context，免费）
- **fallback chain：** lyclaude/gpt-5.5 → b-ai/gpt-5.4 → xiaomi-mimo-2/mimo-v2.5-pro → kiro/claude-sonnet-4.6 → nvidia/llama-3.3
- **0G Router：** `https://router-api.0g.ai/v1`，key 在 `~/.openclaw/openclaw.json` 的 `tokenrouter` 和 `minimax-m3` provider
- **⚠️ TokenRouter 余额 $0（2026-06-17）**：已切到 0G Router 替代
- **⚠️ 双 provider 同步坑**：改 MiniMax M3 配置要同时改 `minimax-m3` 和 `tokenrouter` 两个 provider，否则 session 走的是没改的那个（2026-06-17 踩坑）
- **cron 任务模型：** LongCat-2.0-Preview（isolated agent 环境用主会话模型更稳定）
- **⚠️ isolated agent ≠ 主会话环境**：模型 provider 路由可能不一致
- **MiMo API 限制**：Anthropic 端点只返回 thinking 不返回 text，不兼容 Claude Code（2026-06-03 确认）
- **MiMo 双协议**：新加坡节点同时支持 `/v1`（OpenAI）和 `/anthropic`（Anthropic）协议（2026-06-09）
- **Bluesminds API**：`https://api.bluesminds.com/v1`，42 个模型，fallback chain 第一优先级（2026-06-09）
- **lyClaude API**：`https://free.lyclaude.site`，GPT-5.4/5.5 可用（2026-06-09）
- **统一模型代理**：`scripts/model-sync.sh` + `.bashrc` 自动 source + `claude()`/`codex()` wrapper（2026-06-09）

## LLM Wiki (wiki.threel.site)

- **访问**：https://wiki.threel.site（SSL 正常）
- **后端**：Node.js server.mjs，端口 3000，数据 /vol1/1000/dev-projects/synapse/data
- **认证**：API Token = `***`
- **用途**：threely的私人知识库，小七维护 + threely也能写
- **规则**：threely让搜集/处理/整理的东西 → 自动存到 wiki
- **已同步**：23 篇历史工作日记
- **⚠️ 排序 bug**：手写文章同步后跑到最后面，需修复排序逻辑
- **后端修复**（2026-06-09）：SQLAlchemy 2.0 兼容性 + 数据库缺少列，API 恢复 155 篇笔记/373 标签
- **⚠️ 不自启**：需要 root 权限创建 systemd service
- **⚠️ 去重 bug** (6/23): `create_note` 用 md5(content) 去重，但 `_auto_link_note` 异步追加 wikilink 后 content 变 → md5 不同 → 重复创建。workaround: 同步脚本先 search 同 title, 存在则 PUT。待老板拍修复方案 (A/B/C)
- **⚠️ sync_notes.py timeout**: 默认 10s 太短, 大 content 后端处理要 20-30s, 已改 60s

## 微信公众号

### 分工（2026-05-27 确认）
- **公众号A（三页札记）**：小七负责
- **公众号B（故事不过夜）**：Hermes 负责，小七不管

### 凭证与规则
- **公众号A**：AppID `wx97bc84bb54232e27` | AppSecret 见 .env `WECHAT_APPSECRET_A`
- **⚠️ AppSecret 可能过期，推送前先测 token**
- **代理铁律**：unset ALL proxy vars → Python urllib 直连 → 不能用 curl
- **排版**：`<pre>` 内联样式，正文 14px/行高1.9，标题 17px；封面 900x506 JPEG < 64KB
- **写作**：口语化、去AI化；正文不加 h1；结尾必须有钩子
- **结尾铁律**：引导关注写「每天」，不写「每周」（公众号每天更新）
- **待发布**：银河麒麟 V10 维护避坑指南草稿（5/24 创建）

## NAS 事件推送

- **容器**：fn-message-bot，端口 818 | **Bot**：@xiaozht_bot（Chat ID：460212872）
- **监控**：nas_telegram_monitor.py 监听 logger_data.db3 → SSH 登录、CPU/内存/磁盘告警 → Telegram

## Claude Design Card（封面图生成主力）

- **技能**：`skills/claude-design-card/SKILL.md`（195 stars）
- **功能**：14 种格式 HTML 卡片 → Playwright 截图为 PNG
- **核心格式**：公众号首图（900×383）、视频号/小红书（1080×1440）、抖音（1080×1920）
- **设计语言**：暖色调（Terracotta #c96442）、衬线标题、书籍级行高
- **正文排版**：从第 8 篇起，正文也用 Claude Design Card 设计语言

## 新增项目（2026-05-25~06-03）

- **Superpowers 框架**（06-03）：14 个技能，brainstorming→planning→subagent-dev→TDD→debugging
- **Addy Osmani Agent Skills**（06-02）：23 个生产级工程技能（47.9K stars）
- **ECC Skills**（05-30）：249 个（198K stars），写作/研究/开发/运维/安全
- **AI Sentinel Pro**：Flutter 移动端 LLM Tool Call Monitor
- **GitHub Trending 看板**：dashboard.threel.site
- **360 补丁自动化**：`scripts/360patch.py`
- **Flowsint OSINT**、**browser-use**、**ricoui-astro-starter**、**OpenClaw Android 中文化**

## 安全规则

- **API Key：** 统一放 `~/.openclaw/.env` 和 `~/.bashrc`
- **NAS 禁令：** ❌ 禁止操作 `/usr/trim/` 下任何文件
- **Docker：** 可改容器配置，❌ 不能改 Docker 本身配置
- **备份：** 重要变更后立即备份到 `/vol1/1000/openclaw/backup/`

## Telegram 稳定性模式（重要！）

- **根因**：长对话（如 Pi Agent 安装 + API Key 调试）→ context 90%+ → 模型响应变慢（5-15s）→ Telegram socket 超时断开（UND_ERR_SOCKET）
- **症状**：sessions.list 5-8s、chat.history 15s+、event loop 阻塞 7s+
- **解决**：`/new` 开新 session 清掉 context
- **预防**：长对话后主动提醒threely `/new`
- **已多次发生**：2026-05-28 一天内崩了 3+ 次

## MCP SSE 代理（2026-06-05 修复）

- **问题**：两个 nginx master 进程抢 443 端口，旧 worker 用旧配置处理请求，`location /sse` 不生效
- **修复**：杀掉旧 worker + 用 `location = /sse` 精确匹配（最高优先级）
- **结果**：`https://wiki.threel.site/sse` → event: endpoint ✅ 外网可访问
- **MCP 配置**：移除 mount_path，直接用 `/sse` 路径
- **其他 Agent 连接**：`{"mcpServers:{"wiki":{"url":"https://wiki.threel.site/sse","headers":{"Authorization":"Bearer ***"}}}}`

## 重要经验教训

- **WeChat API 代理铁律**：unset ALL proxy vars → Python urllib 直连 → 不能用 curl（已踩坑 3+ 次！）
- **Telegram socket 超时**：长对话 context 撑满 → 模型响应慢 → socket 断开 → `/new`（详见上方稳定性模式）
- **isolated agent 环境差异**：模型 provider 路由与主会话不同，定时任务需用主会话模型
- **输出前验证完整性**：不要基于部分信息交付（GPT-Image-2 教训）
- **大文件下载**：应在 NAS 终端执行，不要从远端服务器下载
- **nginx SNI**：修改后需完全重启（stop+start），不能只 reload
- **Telegram NO_PROXY**：`NO_PROXY` 里不要包含 `api.telegram.org`，除非确认服务器可直连 Telegram（2026-06-05 踩坑）
- **nginx 双 master**：修改配置后旧 worker 可能仍在用旧配置，需先停 gateway 再重启（2026-06-05 MCP 修复）
- **NVIDIA Embedding**：不能用 nvidia provider，需 openai-compatible + 显式 base URL
- **web_search 不可用**：web_fetch 直接抓站点是可靠备选方案
- **模型限流**：多模型同时限流时 assistant turn 会失败
- **Chromium 反复崩溃**：Gateway 重启后 Chromium 多次挂掉，auto-restart 能恢复但根因未查
- **Flutter import 必查**：本地无 Dart SDK，提交前用 `grep` 抓所有类型名核对 `import` 块，避免 CI 报 `Type 'X' not found`（2026-06-12 踩坑，f​olders_screen.dart 缺 note.dart）
- **听老板反馈先看图**：描述 UI 颜色/布局问题时，图比文字清楚。不要凭关键字过早下结论（6/23 TopBar 白字事件，连听错两次才看图确认）

## 飞牛 NAS Telegram 推送格式（2026-05-28 更新）

- **格式**：`📱 飞牛NAS · APP登录 ✅` + 字段标签（时间/用户/ISP/位置）
- **三种类型**：📱 APP登录、🌐 网页登录、🖥️ SSH登录/SSH登录失败

## 定时任务管理（2026-06-03 更新）

- **工作总结**：从 cron 改为手动 Skill 触发，threely说「总结一下工作」时执行
- **彩票平台数据**：已归档（多天未更新，无后续行动）
- **daily-ai-skills-search**：已禁用（连续 4 天超时失败）
- **horizon-daily-news**：已禁用，改为 skill 手动触发
- **必要 cron**：仅保留 heartbeat、memory-dreaming 等核心任务

## APP 更新机制（2026-06-02 设计）

- **方案**：APP → 服务端（wiki.threel.site）→ 拉 GitHub Release APK → 推送给 APP
- **原因**：APP 无法直连 GitHub（需代理），服务端可以
- **域名**：wiki.threel.site（已有 SSL 证书）
- **版本**：synapse-v2.2.15+57
- **⚠️ 版本号铁律**：每次 feature push 前必须 bump pubspec.yaml 版本号，否则 GitHub Actions 会把 APK 上传到旧 Release

## 📱 iptv-app 版本号铁律（2026-06-23 threely拍）

**格式**：`v{MAJOR}.{MINOR}.{PATCH}.{BUILD}` 四位，pub.yaml 用 `X.Y.Z+B` 语义

**迭代规则**（老板明确指示 6/23 06:30）:
- **第 4 位 (build) = 默认迭代位** — 任何 hotfix / 改小 / 修 bug 都加 1
  - `v0.3.9+1` → `v0.3.9+2` → `v0.3.9+3` ... 
  - 标签: `v0.3.9.1` → `v0.3.9.2` → `v0.3.9.3` ...
- **第 3 位 (patch) = 老板明确说"大版本"才迭代** — 加新功能 / 大改动
  - `v0.3.9` → `v0.3.10` → `v0.3.11` ...
- **第 1/2 位 (major/minor) = 极少动** — 重大重构 / 协议变更

**等价语义**:
- `0.3.9+0` = `v0.3.9` （最初始）
- `0.3.9+1` = `v0.3.9.1` （第 1 次 hotfix）
- `0.3.9+2` = `v0.3.9.2` （第 2 次 hotfix）
- `0.3.10+0` = `v0.3.10` （新功能版）

**release.yml 触发**: tag push `v*` 自动 build APK + 创建 release page

**发布流程（iptv-app）**:
1. subagent push fix commit
2. 主 agent: `sed -i` pubspec bump build +1
3. 主 agent: `git commit + push` 触发 sources sync
4. 主 agent: `git tag vX.Y.Z.B + push` 触发 release.yml
5. release.yml build APK + 创建 release page (asset: APK + sha256)
6. 主 agent: 下载 + sha256 校验 + 备份到 `/vol1/1000/openclaw/backup/iptv-app/` + 通知老板

**⚠️ release page 失败补回**: release.yml 失败时 tag 在 remote 但 release page NOT FOUND，需要 `gh release create vX.Y.Z.B --title --notes` 手动补（6/23 v0.3.9 教训）

**main ↔ beta 同步策略**（6/23 threely拍）:
- 测好一个 release 后，main 同步到 beta 分支
- 同步方案: `git checkout beta && git reset --hard origin/main` 强制指向 main head（保留 main 完整 history, 丢 beta 老 history）
- 之后 beta 跟 main 一起维护，加新功能在 main 上做

## 视频号生活妙招（2026-06-04 启动）

- **赛道**：生活妙招，面向中老年受众
- **项目目录**：`/vol1/1000/video-lifetips/`
- **技能**：`skills/video-lifetips/SKILL.md`
- **工具链**：edge-tts + playwright + ffmpeg，全自动流水线
- **选题库**：30+ 选题，覆盖衣物、厨房、冰箱、省钱、家居
- **第一期**：白衣服发黄（已完成，视频 647KB）
- **节奏**：每天1条，连续7天打标签权重
- **6/8 新验证**：Pillow 分镜图 + edge-tts 配音 + ffmpeg 合成 → 80年代陕北视频成品（2.8MB/41秒），流水线复用成功

## Pixel2Motion 铁律（2026-06-14 threely拍: "以后画图/做 logo 都用这个, 每次手搓太丑了"）

### 安装路径
- **本地**：`/home/liyang/.openclaw/workspace/skills/pixel2motion/`（6.8MB，已 git clone 删 .git）
- **原仓库**：[nolangz/pixel2motion](https://github.com/nolangz/pixel2motion) (249 ⭐, MIT)
- **依赖**：`python3 -m venv .venv && .venv/bin/pip install pillow numpy playwright && .venv/bin/python -m playwright install chromium`

### 三步工作流
- **Phase 1 PIXEL**: 读图 + 写 motion_spec.md (personality 词 + 编排草图)
- **Phase 2 VECTOR**: PNG → 最简光滑 logo.svg（不要手画！）
- **Phase 3 MOTION**: SVG + CSS → logo_motion.html (带 replay/慢放/速度控制)

### threely最常用 3 个命令
1. **出 HTML 演示页**：`animate_svg_showcase.py logo.png --out /tmp/motion.html --duration 1500`
2. **导出 MP4**：`capture_motion_frames.py` + `ffmpeg -framerate 30 -i /tmp/frames/%d.png -c:v libx264 -pix_fmt yuv420p out.mp4`
3. **导出 GIF**：`capture_motion_frames.py` + `ffmpeg -framerate 12 -i /tmp/gif_frames/%d.png -vf "scale=600:-1" out.gif`

### threely铁律 (KEEP 永远)
- **❌ 别手绘矢量图标了**（v0.3.31 教训：596 行自绘 FileTypeIcon.kt 被吐槽"丑"）
- **❌ 别手画 SVG logo 了**（Pixel2Motion Phase 2 自动拟合 + QA 比手画精准）
- **✅ 任何 logo / 矢量 / 动效任务 → 直接用 Pixel2Motion**

### 知识库同步 (6/14 23:00)
- **#225** Pixel2Motion threely版 - PNG 像素 logo 转品牌动效
- **#227** Pixel2Motion OpenClaw 技能版 (SKILL 索引)
- **同步脚本**：`scripts/sync_pixel2motion_wiki.py`（直接 POST /api/notes，**不要用 search 查重会 timeout**）

## DESIGN.md — 视界设计系统文档 + 通用技能（2026-07-08 创建）

- **通用技能**：`skills/design-md-generator/SKILL.md` — 任何项目可用，告诉 agent 怎么写/用 DESIGN.md

- **路径**：`/vol1/1000/dev-projects/sanyelive/DESIGN.md`
- **格式**：Google Stitch DESIGN.md 标准（colors/typography/rounded/spacing/components + 章节说明）
- **用途**：AI agent 生成 UI 时读此文件，输出 UI 时读此文件，输出自动匹配"视界"设计语言\n- **来源**：`github.com/VoltAgent/awesome-design-md`（73 个品牌参考）\n- **覆盖**：浅色/暗色双色板、7 级字体层级、10 个组件定义、TV/手机双端响应式、焦点动画、Do's & Don'ts\n- **规则**：任何 agent 做 iptv-app UI 相关工作前，必须先读 DESIGN.md\n\n## iptv-app 近期版本历史 (6/23)"}]

- **v0.3.9.2** (6/23 06:39 发布): ipv4栈溢出fix + Pixel2Motion splash + TopBar白字fix
- **v0.3.9.3** (6/23 EPG时区fix pushed, 等tag): commit 348e604, UTC→Beijing local
- **版本号铁律**: build位默认迭代, patch位老板说"大版本"才动

## 资源收藏

### Public APIs 集合（2026-07-04 记录）
- **Repo**：[public-apis/public-apis](https://github.com/public-apis/public-apis)（300K+ stars）
- **用途**：整理了大量免费公共 API，以后做项目可以参考
- 涵盖 AI/LLM、天气、数据、工具等多个分类

## 近期重点跟踪事项

### 知识库 APP 功能扩展（2026-06-08 完成）
- **统计面板**：总笔记/标签/阅读量/时长 + 日趋势柱状图 + 热门笔记 Top10
- **分类管理**：文件夹 CRUD + 6色选择器 + 笔记分类分配
- **通知中心**：未读计数 + 全部已读 + 删除 + 设置开关
- **入口集成**："我的"页面 3 个导航卡片 + 首页统计卡片 + 底部导航通知角标
- **图标**：Pillow 生成 5 种分辨率 PNG（mdpi~xxxhdpi），橙色齿轮 + 白色圆形背景
- 版本：v2.2.37+79 → beta 构建中

### sub2api 改为本地构建（2026-06-08 确认）
- threely明确说不用 Docker 部署，Docker 容器已清理
- 通过 gh CLI 下载 release 二进制到 `/vol1/1000/dev-projects/sub2api-src/`
- 需要 PostgreSQL + Redis + nginx 反向代理配置
- ⚠️ GitHub 网络不通（GnuTLS recv error），等恢复后拉源码

### sub2api 本地化部署 (2026-06-15 threely拍)
- 路径: `/vol1/1000/dev-projects/sub2api/` (threely规则, 不在 /opt)
- binary: `/vol1/1000/dev-projects/sub2api/sub2api` (v0.1.135, threely 6/9 编译)
- systemd: `sub2api.service` (DATA_DIR 环境变量, viper 找 config.yaml)
- PostgreSQL: 本机 PG 15, 库 `sub2api`, user `sub2api` (密码从 .env)
- Redis: 本机 Redis 7.0.15, no password
- nginx: `/etc/nginx/conf.d/model.threel.site.conf` (反代 8080)
- 域名: `https://model.threel.site`
- admin: `admin@sub2api.local` / 密码从 `/vol1/1000/dev-projects/sub2api/deploy/.env`
- API base: `/api/v1` (login: `/api/v1/auth/login`, setup: `/setup/status`)
- 业务数据: 183 schema_migrations + 6943 ops_system_metrics + 1 user + 33 settings + 8 alert rules
- 备份: dump 在 `/vol1/1000/dev-projects/sub2api/dump/`
- Docker 状态: 引擎保留, 容器全删 (万一以后用)
- 系统分区: 45G → 41G (省 4GB)

### sub2api 真实状态修正 (2026-06-15 19:48 threely反馈)
- 之前 MEMORY 6/8 "不用 Docker" 是 stale:
  - 5/24 threely用 docker-compose 搭了 sub2api (`/home/liyang/sub2api-deploy/`)
  - 6/10 创建容器, 6/12 启动, 跑了 3 天没停
  - 6/8 "不用 Docker" 可能只针对源码编译版 (`sub2api-src/`), **不是**清掉运行中的容器
  - 实际 Docker 没清理, 反而在用
  - **6/15 threely拍板: 不用 Docker, 本地化部署**
  - 现在: 容器全删, sub2api 跑在本机 systemd + nginx 反代 model.threel.site

### 视频制作流水线（2026-06-08 验证）
- **方案**：Pillow 分镜图 + edge-tts 配音 + ffmpeg 合成
- **成品**：80年代陕北视频 2.8MB，41 秒，6 张分镜图 + 6 条配音
- 可复用于视频号生活妙招后续期

### Gateway 绑定地址问题（2026-06-08 发现）
- Gateway bind 已改为 `lan`（绑定 0.0.0.0:18789）✅（2026-06-09 修复）
- ⚠️ 手机移动数据 IPv6 仍不稳定（DNS AAAA 记录存在但连接失败）
- 待解决：ai.threel.site 的 IPv4 A 记录

### 工作总结同步规则（2026-06-03 确认）
- 「工作总结」→ 同步**知识库 + IMA 笔记**，缺一不可
- 顺序：① wiki.threel.site `/api/notes` → ② ima.qq.com `/openapi/note/v1/import_doc`
- 凭证：`~/.config/ima/client_id` + `~/.config/ima/api_key`

### P0 紧急
- **Telegram 稳定性**：长对话后 context 撑满导致 socket 断开，已多次发生。需主动管理 session 生命周期
- **AppSecret 过期风险**：最后更新 2026-05-22，已知频繁过期。建议：推送前先测 token 接口，失败则通知threely
- **Hermes 不响应**：2026-05-31 threely反馈 Hermes (@thinkpa_bot) 不回复消息，**连续 5 个梦境未排查** ⚠️（已 stale，如threely未再提及则下次移除）
- **Wiki 排序 bug**：手写文章同步后跑到最后面，需修复
+ **Hermes 不响应**：2026-05-31 threely反馈 Hermes (@thinkpa_bot) 不回复消息，**连续 6 个梦境未排查** ⚠️（已 stale，如threely未再提及则下次移除）
+ **Wiki 排序 bug**：手写文章同步后跑到最后面，需修复
+ **知识库 APP 版本**：v2.2.37+79（2026-06-08），beta 构建中
+ **iptv-app 当前版本**：v0.3.9.2 (6/23 发布)，main 上有 EPG 时区 fix (348e604) 待打 tag v0.3.9.3
+ **模型切换中断风险**：切换默认模型时误写字符串破坏 fallback 链（2026-06-09），已修复
- **Wiki 排序 bug**：手写文章同步后跑到最后面，需修复

### P1 重要
- **Android APK 卡 logo**：需重新编译（待threely确认）
- **Chromium 反复崩溃**：Gateway 重启后多次挂掉并自动恢复，根因未查

### 已完成（5/27~6/3）
- 推文+Linux系列(8篇)+MiMo 800亿key+Synapse v2.2.15+Wiki systemd+Addy Osmani技能+Docker代理 ✅

## v0.3.4 OpenList Android APP 修复 (6/14)
- **下载 401 根因**: /d/<path> 路由只查 ?sign= 不看 Authorization, 改用先 POST /api/fs/get 拿 sign
- **上传 400 'storage not found' 根因**: FsForm 源码读 File-Path header 不读 query, 改用 PUT /api/fs/form + File-Path: <路径> + As-Task: true
- **液态玻璃弹窗**: Material 3 Dialog + 半透明白 (alpha 0.85) + 24dp 圆角 + 12dp 阴影 + 操作行重设计
- **踩坑**: KSP 跟 KDoc 里 [xxx] 方括号冲突报 Unclosed comment, 改用纯 ASCII 标点
- **释放**: v0.3.4 APK 1.79MB (sha256 29466ff7...) 同步到 fn.threel.site latest.json + changelog.json, force_update=true

## 踩坑教训: Android / Flutter 项目本机不构建
- threely 6/14 严厉: "我在本地装 Android SDK 吗？代码不是在 GitHub 上吗？占用内存空间"
- 铁律: APP 项目 (Android/Flutter/iOS) → 改代码 push → CI 拿 APK, 永远不在本地装 SDK/Gradle/JDK/Flutter
- 释放了 290MB 本地垃圾 (gradle-8.10.2-bin 137MB + commandlinetools-linux 153MB)


## 2026-05-30~06-03 工作摘要

- **模型**：LongCat → deepseek-v4-flash → mimo-v2.5-pro（800亿 key），MiMo 1M context 修复
- **Linux 系列**：8篇（Vim已发布，7篇草稿箱）
- **Synapse v2.2.15**：OTA 流式下载+进度条+自动安装
- **NAS 禁令再犯**：尝试改 Trim nginx 被制止（需更快自检）
- **OpenClaw 更新**：2026.6.1-beta.3 → 2026.6.2-beta.1

## dev-projects 项目规范

- **位置**：`/vol1/1000/dev-projects/`
- **规则**：一个项目一个子目录，各自维护 README，nginx 独立配置，端口独立分配，数据文件项目内自治
- **新建项目**：在 dev-projects/ 下创建独立子目录，创建 README.md，按需配置 nginx 和端口

## Cloudflare

- **API Token：** `CF_API_TOKEN`（~/.openclaw/.env）
- **Account ID：** `1caaacb82c8c6a0d441ef9a803f2e640`

## TTS 语音配置

- **小米 MiMo TTS**：新加坡节点 `https://token-plan-sgp.xiaomimimo.com/v1`，音色 Mia
- **Microsoft TTS**：`zh-CN-XiaoxiaoNeural`（edge-tts 备选）

## OpenList

- **容器**：`openlist`，端口 5244，数据 `/vol1/1000/openlist/data`
- **功能**：AList 分支，多盘聚合（阿里云盘、百度网盘等）



## Archived (stale)
<!-- photon集成, Anthropic-Security, xhs-cli, Mihomo密码, 彩票数据源, Hermes不响应 -->

## OpenList 网盘（2026-06-13）

- **服务地址**：`http://127.0.0.1:5244`（内网）/ `https://fn.threel.site/`（公网）
- **登录**：`liyang` / `Sanyun2026!`（2026-06-13 threely要求重置，**原 admin 账号已被threely改成 liyang**）
- **systemd**：`/etc/systemd/system/openlist.service`，`WorkingDirectory=/vol1/1000/openlist`，`OPENLIST_DATA_DIR=/vol1/1000/openlist/data`
- **重要踩坑**：`openlist admin set` 命令**必须 `cd /vol1/1000/openlist` 跑**，**不然改了空 db**（pwd 错时日志会显示 `reading config file: <错的>/data/config.json`）
- **systemd 启动**：`sudo systemctl restart openlist`（不是 `openlist start` 也不是 kill master，**systemd 在守护**）
- **进程特点**：双进程共存（admin set 子进程 + systemd server），**杀时只杀 admin set 的那个**（带 `--force-bin-dir`）
- **API 验证登录**：`curl -X POST http://127.0.0.1:5244/api/auth/login -H "Content-Type: application/json" -d '{"username":"liyang","password":"Sanyun2026!"}'` → `200 success + token`
- **APP 端 default server**：`https://fn.threel.site`（`/vol1/1000/dev-projects/openlist-android/app/src/main/java/.../TokenStore.kt` 里 `DEFAULT_SERVER`）
- **APP 升级 API**：`/api/openlist-android/latest.json` + `/api/openlist-android/changelog.json`（用 `fn.threel.site` 域名）
- **反代 nginx**：`/etc/nginx/conf.d/fn.threel.site.conf`（**root 反代到 127.0.0.1:5244**，`/api/openlist-android/` 是 alias serve 静态 JSON）
- **nginx reload 铁律**：`sudo systemctl restart nginx` 而不是 `nginx -s reload`（**systemd 守护**——`nginx -s stop/reload` 经常不生效，老 worker 仍 listen）
- **完整登录链**：① `https://fn.threel.site/` → ② Debian nginx (`/usr/sbin/nginx`) → ③ reverse_proxy `127.0.0.1:5244` → ④ OpenList systemd server

## OpenList 密码算法（2026-06-13 排坑，threely要求记录）

- **算法**：`PwdHash = sha256(sha256(pwd + "-" + StaticHashSalt) + "-" + salt)`
  - 注意分隔符是 `-` 不是 `+`
  - `StaticHashSalt = "https://github.com/alist-org/alist"`
  - `salt` 是 db 里 x_users.salt 字段（admin set 时随机生成 16 字符）
- **OpenList 4.x 源码**：`internal/model/user.go` 的 `TwoHashPwd(pwd, salt)` 函数
- **Login 流程**：
  1. `req.Password = StaticHash(req.Password)` = `sha256(pwd + "-" + StaticHashSalt)`
  2. 比对 `HashPwd(staticHash, salt) == user.PwdHash`

## OpenList 踩坑清单（2026-06-13 总结）

- **`openlist admin set` 必须 `cd /vol1/1000/openlist`** —— 不然改了空 db（systemd 跑的真 db 没改）
- **`admin set` 不改 `password` 字段**（只改 pwd_hash + salt）—— 但不影响 login
- **登录限流**：同 IP 5 次错 → `429 Too many attempts` 5 min lockout
  - 限流期间 login API 返回 **`code:401, message: "Too many..."`**（**不是 429**）
  - 清限流：`sudo systemctl restart openlist`（LoginCache 是 in-memory）
- **nginx reload 铁律**：`sudo systemctl restart nginx`（systemd 守护）—— `nginx -s reload` 不一定生效（双 nginx master 抢端口）
- **fn.threel.site 域名铁律**：root **必须**反代 `127.0.0.1:5244`（OpenList），`/api/openlist-android/` 是 alias serve 静态 JSON
- **trim nginx 不抢 443**：飞牛 trim_nginx.service 只 listen 5666/5667（管理口），443 是 Debian nginx（systemd）管的

## fn.threel.site（2026-06-13 拍定：就是给threely访问的域名）

- **用途**：OpenList 网盘前端 + APP 升级 API
- **内网**：`http://127.0.0.1:5244`
- **公网**：`https://fn.threel.site/`
- **APP 默认 server**：`https://fn.threel.site`（TokenStore.DEFAULT_SERVER）

## Claude Fable 5 Prompt (2026-06-14 threely 21:00 任务)

> 来源: GitHub `elder-plinius/CL4R1T4S` 仓库 `ANTHROPIC/CLAUDE-FABLE-5.md`
> 完整系统 prompt 1585 行 / 120KB / 15 sections / 55 subsections
> 是 Anthropic 推出的 **Claude 5 系列**首发模型 (Mythos-class 层级, 高于 Opus 4.8) 的系统提示词泄露版

### 工作区文件

- 原文 (英文完整版): `drafts/claude-fable-5/CLAUDE-FABLE-5-original.md` (120KB, 1585 行)
- 中文翻译整理版: `drafts/claude-fable-5/CLAUDE-FABLE-5-CN.md` (~500 行, 27.6KB)
  - 翻译策略: 摘要 + 关键 sections 直译, 跳过完整 Tool Definitions (机器代码) + 重复 examples
  - 必翻 sections: claude_behavior / memory_system / persistent_storage / mcp_app_suggestions / computer_use / search_instructions / using_image_search_tool
  - 保留所有 code block / 工具调用示例, 保留英文专有名词 (Claude Fable 5, Mythos, Opus, Sonnet, MCP 等), 章节标题跟原文一一对应

### 知识库 (2026-06-14 21:00 POST)

- **CN 翻译整理版** (note_id=**223**, slug=20260614003)
  - title: "Claude Fable 5 系统 prompt 中文翻译整理 (1585 行原文 摘要版)"
  - tags: claude, claude-fable-5, prompt, anthropic, 知识库, AI Agent, 系统提示词
- **原文完整版** (note_id=**224**, slug=20260614004)
  - title: "Claude Fable 5 完整系统 Prompt (1585 行原文)"
  - tags: claude, claude-fable-5, prompt, anthropic, 原文, 系统提示词

### 关键 takeaway (给threely/我们用)

1. **理解 Claude 脾气**: claude_behavior + tone_and_formatting + user_wellbeing 是核心
2. **Computer Use 范本**: skills 强制读 → 创建策略 → 分享三段式
3. **MCP 伦理**: third-party 必须 suggest → 让用户选, 不替用户选 partner
4. **版权硬限**: 15 词 / 1 源 1 quote / 完整作品不碰, 所有 agent 都应学
5. **artifact 边界**: 什么时候建文件 vs inline; docx 成本高要谨慎; ⚠️ 绝不用 localStorage in artifacts
6. **Claudeception**: 在 artifact 里调自家 API 做"AI-powered apps"
7. **关键反模式**: ❌ 假工具/假 UI (Imagine) / ❌ 替用户选 partner / ❌ 用 bullet 在拒绝时 / ❌ 给"自伤替代"技巧 / ❌ 替用户做财务/法律推荐

## Workboard 状态机坑（2026-06-17 踩）
- ❌ `workboard_create(parents: [父id])` 会自动 link parent→child, 子卡被 'card dependencies are not done' 锁
- ❌ `workboard_claim` 不接受 force 参数, 直接撞 'dependencies not done'
- ✅ 修法: 父卡先 `workboard_complete` 标 done (带 createdCardIds 引用子卡), 子卡才能 promote ready → claim
- ✅ 或者: 子卡直接用 `workboard_promote(force: true)` 跳过依赖检查
- ❌ 父子卡 + sessions_spawn 派 subagent 是两套状态, 别混用
- ✅ 正确路径: workboard_dispatch 自动派 worker (带 claim token), 让 subagent 自己 heartbeat / complete

## MiMo Credits 分享额度 (2026-06-17 threely拍)
- **6+1 个 token-plan 码, 共享额度, 到期时间不等**:
  - 3500亿 `tp-svf2ap41dvitec7awprrnnljawy82yjbhtu9m6cwz6uh4xme` (主用, 6.27 到期)
  - 380+110亿 ×3 个 (failover)
  - 820+240亿 ×2 个 (failover)
  - 800亿 `tp-cameb6uz1nunv92bqr8z9yqxfnbkeeapjit94wetkq2rcis1` (7.2 到期)
- **Base URL**: OpenAI 协议 `https://token-plan-cn.xiaomimimo.com/v1`
                Anthropic 协议 `https://token-plan-cn.xiaomimimo.com/anthropic`
- **已写入** `~/.bashrc` 导出 MIMI_CREDITS_* / MIMI_BASE_URL*
- **需要测试**: 7 个码都跑一次, 看哪个稳定

## 公众号 Cursor 之死 草稿已推送 (2026-06-17 20:46)
- 标题: Cursor之死：40亿流水买不来护城河
- media_id: iVozxhozJX8kpyJxwkVrz9nInKzchIIp2hYs0iSnMdxeVRrL7QPr2POBfuRp9VXF
- 状态: 草稿箱, 等threely看
- 知识库同步遇到 API 超时

## Fallback Chain 修复 (2026-06-17 21:00)
- **primary**: `tokenrouter/minimax-m3` (0G Router, 6/22 前免费, 1M context)
- **fallbacks** (顺序, 5 个):
  1. `lyclaude/gpt-5.5` (LyClaude, OpenAI)
  2. `b-ai/gpt-5.4` (B.AI, OpenAI)
  3. `xiaomi-mimo-2/mimo-v2.5-pro` (800亿码, OpenAI 协议)
  4. `xiaomi-mimo-anthropic/mimo-v2.5` (800亿码, Anthropic 协议, reasoning)
  5. `nvidia/meta/llama-3.3-70b-instruct` (NVIDIA 备用)
- **摘掉**: `kiro/claude-sonnet-4.6` (402 余额不足)
- **摘掉**: `b-ai/claude-opus-4.6` (同问题)
- **8G Router key 路径**: `models.providers.minimax-m3.apiKey` & `tokenrouter.apiKey` (同一 key, baseUrl 都是 `router-api.0g.ai/v1`)
- **8G Router baseUrl**: `https://router-api.0g.ai/v1` (不是 tokenrouter.com!)
- **mimo-v2.5-pro 推理**: `reasoning: false` (直接出 text, 不吃 max_tokens)
- **mimo-v2.5 推理**: `reasoning: true` (给 max_tokens ≥500)
- **mimo-v2.5-pro latency**: ~11-16s (慢, 但有回复)
- **mimo-v2.5 (anthropic) latency**: ~2s (快)

## MiMo 多通道 (2026-06-25)

- **新加坡直连** `xiaomi-mimo/mimo-v2.5` ✅（NO_PROXY 已配，gateway 直连）
- **Bynara 代理** `bynara/mimo-v2.5-free` ✅ 免费 | `bynara/mimo-v2.5-pro-free` ✅ 免费
- **MiMo Token Plan**：`tp-cq8wq3s4ixj5t08cklnf4pqsmq89wvtmyq6pv9zi1wzua9om`（2026-06-25 分享）
  - Anthropic 协议：`https://token-plan-cn.xiaomimimo.com/anthropic`
  - OpenAI 协议：`https://platform.xiaomimimo.com`
- **域名**：`router.bynara.id`（不是 `api.bynara.com`，后者 NXDOMAIN）
- **额度**：Bynara MiMo 每天 700M 免费调用
- **⚠️ bynara/mimo-v2.5-pro 余额 $0**（不是 pro-free），不要用

## MiMo 6 失效码 (2026-06-17 21:00 验证)
- 3500亿/380+110×3/820+240×2 → **全 401 Invalid API Key** (过期/被注销/余额 0)
- 6 失效码已从配置移除, 只留 800亿那个

## minimax-m3 双平台坑 (2026-06-17)
- **历史误读**: 我之前以为 mimo 平台有 minimax-m3, 实际没有
- **threely原意**: 0G Router (primary) + 小米 mimo (fallback) 两个不同平台都接好
- **正解**: minimax-m3 只在 0G Router 上, fallback 走 mimo (mimo-v2.5-pro/v2.5/omni) 不是 m3

## Promoted From Short-Term Memory (2026-08-31)

<!-- openclaw-memory-promotion:memory:claim:a4d8c88cf0d0 -->
- 结论: **无严重问题**，无需通知 threely。 [score=0.835 signals=7 recalls=0 avg=0.620 source=memory/2026-08-27.md:25-25] <!-- trigger: 结论, 严重, 问题 --> <!-- importance: 8 -->
