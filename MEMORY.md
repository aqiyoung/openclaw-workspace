# MEMORY.md — 小七的长期记忆 🤖

> 上次梦境更新：2026-05-17。目标：保持在 200 行以内，索引而非堆砌。

## 关于老板

- **名称：** Young，喜欢被叫"阳仔"
- **技术背景：** 运维工程师，熟悉 Linux、飞牛NAS、信创系统、nginx、docker、mihomo 代理
- **沟通风格：** 直接、不废话、偏好技术交流

## 账号信息

- **Telegram：** @XNM_SHR (ID: 460212872)
- **飞书 open_id：** ou_3c1068d79dee7c0e06ffb89eb461aed7
- **NAS 服务器：** threelnas (192.168.31.58)

## 模型配置

- **主模型：** LongCat-2.0-Preview（不带 provider 前缀）
- **cron 任务模型：** LongCat-Flash-Lite
- **内容代理模型：** LongCat-Flash-Chat
- **✅ 标准化完成：** 所有 7 个定时任务和 content agent 均使用裸模型名，HTTP 200 验证正常
- **✅ 标准化完成：** 所有 7 个定时任务和 content agent 均使用裸模型名，HTTP 200 验证正常

## 飞书群组

- **牛马公司** (oc_34f560ad2af0a629b9ef9ae189ba7a63)

## 已安装的技能

- **github / gh-issues / github-ops** — GitHub 操作
- **ima-skill** — 艾玛笔记管理（API 认证问题待解决）
- **wechat-mp-writer / wechat-mp-publisher** — 微信公众号写作与发布
- **huashu-design** — 设计生成
- **agent-dream** — 梦境系统（每日 3:00 AM）
- **✅ 内容代理 agent** — horizon-daily-news 等内容的采集推送
- **✅ CLI-Anything** — 76 个 Agent 原生 CLI 工具市场，已安装 16 个（feishu/drawio/mermaid/exa/n8n/zotero/chromadb/dify-workflow/pm2/wiremock/anygen/mubu/adguardhome/firefly-iii/seaclip/videocaptioner）
- **✅ 内容代理 agent** — horizon-daily-news 等内容的采集推送
- **✅ CLI-Anything** — 76 个 Agent 原生 CLI 工具市场，已安装 16 个（feishu/drawio/mermaid/exa/n8n/zotero/chromadb/dify-workflow/pm2/wiremock/anygen/mubu/adguardhome/firefly-iii/seaclip/videocaptioner）

## 老板的暗号

- **小龙虾** = OpenClaw

## 关键发现

- **模型切换面板部署完成** — 从 0 到 1 部署外部端面板，支持手机浏览器调试 OpenClaw 模型调用
- **NAS事件推送日期bug修复** — 修复了 SSH 登录通知显示错误日期的问题
- **AppSecret 频繁失效** — 从 4月24日起就失效，今天下午短暂恢复后又失效，需要重新生成
- **Gateway 重启成功** — 通过 Telegram 报告 "gateway 重启成功"（硬规则）
- **TTS 语音配置完成** — 小米 MiMo 新加坡节点 + Microsoft TTS 备选
- **NAS 监控优化** — 本地 Python 脚本 + nginx 日志监控，正常运行
- **IMA 笔记 API 正常工作** — 知识库「小龙虾🦞运维日记」可读写，但需补充关联步骤

## 微信公众号 AppSecret 管理

- **AppSecret 频繁失效** — 从 4月24日起就失效，今天下午短暂恢复后又失效
- **必须 Python 直连** — curl 走代理会 40125，必须用 Python urllib + requests
- **getAccessToken 接口** — getStableAccessToken 的 token 不能用于素材上传
- **服务器出口 IP：111.19.6.200** — 微信后台白名单必须配这个 IP
- **封面图尺寸：900x506 JPEG < 64KB**（比例 1.78:1），不能复用
- **当前 AppSecret:** `80e6a33afe5287698331cd5aa2248e24`（2026-05-15 更新，已失效）
- **WeChat IP验证**: 服务器出口IP必须匹配微信后台白名单 (111.19.6.200)，不仅是AppSecret有效性
- **解决方案**: 建立自动化监控机制，提前预警凭证过期
- **必须 Python 直连** — curl 走代理会 40125，必须用 Python urllib + requests
- **getAccessToken 接口** — getStableAccessToken 的 token 不能用于素材上传
- **服务器出口 IP：111.19.6.200** — 微信后台白名单必须配这个 IP
- **封面图尺寸：900x506 JPEG < 64KB**（比例 1.78:1），不能复用
- **当前 AppSecret:** `80e6a33afe5287698331cd5aa2248e24`（2026-05-15 更新，已失效）
- **WeChat IP验证**: 服务器出口IP必须匹配微信后台白名单 (111.19.6.200)，不仅是AppSecret有效性
- **解决方案**: 建立自动化监控机制，提前预警凭证过期

## 系统资源约束

- **Gateway 内存紧张** — 总共 3.7GB 内存，可用仅 500MB
- **Whisper medium 模型** 加载会触发 OOM，避免在 gateway 上运行内存密集型任务
- **视频字幕处理** 需要寻找替代方案或分布式处理
- **Whisper medium 模型** 加载会触发 OOM，避免在 gateway 上运行内存密集型任务
- **视频字幕处理** 需要寻找替代方案或分布式处理

## 代理对第三方API的影响

- **问题**: curl 通过 mihomo 代理（127.0.0.1:7890）调用微信 API 返回 40125 invalid appsecret
- **根本原因**: 代理对微信 API 的 POST 请求有影响，导致签名验证失败
- **解决方案**: 改用 Python urllib 直连调用，主动清除 https_proxy/http_proxy 环境变量
- **经验教训**: 第三方API调用时要特别注意代理设置，某些API对代理有特殊要求
- **根本原因**: 代理对微信 API 的 POST 请求有影响，导致签名验证失败
- **解决方案**: 改用 Python urllib 直连调用，主动清除 https_proxy/http_proxy 环境变量
- **经验教训**: 第三方API调用时要特别注意代理设置，某些API对代理有特殊要求

## TTS 节点选择经验

- **问题**: 小米 MiMo API 返回 401 错误
- **排查过程**: 发现 API key 对 token-plan-cn（中国节点）无效
- **解决方案**: 切换到 token-plan-sgp（新加坡节点）后正常工作
- **配置要点**: TTS provider 配置为 xiaomi，API地址必须使用新加坡节点
- **排查过程**: 发现 API key 对 token-plan-cn（中国节点）无效
- **解决方案**: 切换到 token-plan-sgp（新加坡节点）后正常工作
- **配置要点**: TTS provider 配置为 xiaomi，API地址必须使用新加坡节点

## 安全规则

- **API Key：** 统一放 `~/.openclaw/.env` 和 `~/.bashrc`
- **NAS 禁令：** ❌ 禁止操作 `/usr/trim/` 下任何文件
- **Docker：** 可改容器配置，❌ 不能改 Docker 本身配置
- **备份：** 重要变更后立即备份到 `/vol1/1000/openclaw/backup/`
- **Exec 审批：** gateway 自动发 Telegram 按钮审批危险操作
- **Web 控制台：** 新设备需要配对审批

## OpenList

- **容器：** `openlist`，端口 5244
- **数据目录：** `/vol1/1000/openlist/data`
- **功能：** AList 分支，多盘聚合（阿里云盘、百度网盘等）
- **数据目录：** `/vol1/1000/openlist/data`
- **功能：** AList 分支，多盘聚合（阿里云盘、百度网盘等）

## 模型切换

- **方式**：Telegram 命令 `/model`
- **功能**：查看状态、切换模型、测试连通性、重载配置
- **配置文件**：`~/.openclaw/openclaw.json`


## 网络检测工具

- **脚本**：`scripts/network_check.sh`
- **功能**：IP 查询（直连/代理出口）、连通性测试（Ping + HTTPS）、mihomo 状态（版本/节点数/当前节点）、DNS 泄露检测、网站分流测试
- **用法**：`bash scripts/network_check.sh`
- **依赖**：curl、python3、dig（可选）

## Cloudflare

- **API Token：** `CF_API_TOKEN`（~/.openclaw/.env）
- **Account ID：** `1caaacb82c8c6a0d441ef9a803f2e640`

## TTS 语音配置

- **小米 MiMo TTS：** 新加坡节点 `https://token-plan-sgp.xiaomimimo.com/v1`，音色 Mia
- **Microsoft TTS：** `zh-CN-XiaoxiaoNeural`（edge-tts 备选）
- **注意：** 中国节点不能用，gateway 内存紧张（3.7GB）

## 公众号排版规则确认
- 代码块：`<pre>` 直接内联样式，不用 `<style>` 标签，不用 `<pre><code>` 嵌套
- 正文字体 14px，标题 17px
- 封面图 900x506 JPEG < 64KB
- 老板确认这个效果 OK，以后都按这个来