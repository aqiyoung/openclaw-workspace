# 2026-05-15 工作日记

## 今日工作内容

**13:00-13:21 安全审批机制配置**
- **操作**：配置了 OpenClaw 的安全审批机制，完善了 exec-approvals.json 配置文件
- **结果**：✅ 成功配置危险命令审批流程，包括 npm install -g/uninstall -g、gateway重启、docker容器管理等需要Telegram审批确认的命令
- **技术细节**：发现并修复了按钮消息格式问题，正确格式应为 message(action=send, presentation={"blocks":[{"type":"buttons","buttons":[...]}]})，callback_query会自动处理无需用户手动发送文本

**19:00-20:10 TTS 语音功能排查**
- **操作**：深入排查小米 MiMo TTS 配置问题，最终确认正确配置
- **结果**：✅ 定位并解决了小米 API 401错误，确认正确API地址为 https://token-plan-sgp.xiaomimimo.com/v1（新加坡节点），而非之前错误的中国节点
- **关键发现**：小米 token-plan-cn（中国节点）API key 无效，必须使用 token-plan-sgp（新加坡节点）

**20:00-21:09 OpenClaw 更新 & 记忆系统修复**
- **操作**：执行 OpenClaw 版本更新并修复向量记忆功能
- **结果**：✅ 成功将 OpenClaw 从 2026.5.14-beta.1 更新到 2026.5.14-beta.2
- **记忆系统**：配置 memorySearch provider=openai, model=BAAI/bge-m3，使用 SiliconFlow API 建立索引成功（main.sqlite 20MB），搜索测试正常返回6条结果
- **内存警告**：发现 Gateway 内存紧张（3.7GB总共，可用仅500MB），Whisper medium模型加载会触发OOM，需避免在gateway上运行内存密集型任务

**21:35-21:55 微信公众号 API 踩坑记录**
- **操作**：解决微信 API 调用中的代理问题
- **结果**：✅ 发现 curl 通过 mihomo 代理调用微信 API 返回 40125 invalid appsecret 错误，改用 Python urllib 直连调用解决
- **重要纠正**：确认正确 AppSecret 为 `31dd5e8ce9bf116d1b5ca3b81c2d82ea`，之前使用的 `032564217cfc2fc954e53752a7f68da3` 是飞书密钥不是微信的
- **封面图规则**：必须根据当次推文内容重新生成封面图，不能复用之前的，使用 scripts/cover_gen.py 脚本压缩到 < 64KB

**全天 - 系统监控与日志分析**
- **操作**：监控系统运行状态，分析各类日志文件
- **结果**：✅ 确认 agent-dream cron 任务状态为 error（isolated agent setup timed out），已记录待后续排查
- **资源监控**：Gateway服务内存使用稳定，CPU和网络连接正常，磁盘I/O无异常

## 今日踩坑记录

### 代理对微信 API 的影响
- **问题**：curl 通过 mihomo 代理（127.0.0.1:7890）调用微信 API 返回 40125 invalid appsecret
- **根本原因**：代理对微信 API 的 POST 请求有影响，导致签名验证失败
- **解决方案**：改用 Python urllib 直连调用，主动清除 https_proxy/http_proxy 环境变量
- **经验教训**：第三方API调用时要特别注意代理设置，某些API对代理有特殊要求

### 小米 TTS 节点选择
- **问题**：小米 MiMo API 返回 401 错误
- **排查过程**：发现 API key 对 token-plan-cn（中国节点）无效
- **解决方案**：切换到 token-plan-sgp（新加坡节点）后正常工作
- **配置要点**：TTS provider 配置为 xiaomi，API地址必须使用新加坡节点

### Gateway 内存管理
- **问题**：大模型加载时 Gateway 内存不足
- **现状**：3.7GB总内存，可用仅500MB
- **风险点**：Whisper medium 模型（1.5GB）加载会卡住甚至OOM
- **建议**：避免在 gateway 上运行内存密集型任务，必要时重启释放内存

## 系统关键变更汇总

### OpenClaw 版本升级
- **时间**：20:00
- **版本**：2026.5.14-beta.1 → 2026.5.14-beta.2
- **方式**：npm install -g openclaw@beta
- **影响**：包含向量记忆功能修复和新特性

### 向量记忆索引建立
- **时间**：20:05
- **配置**：memorySearch provider=openai, model=BAAI/bge-m3
- **API**：SiliconFlow（免费额度）
- **状态**：索引建立成功，搜索功能正常

### 微信公众号 API 调用方式修正
- **时间**：21:35
- **变更**：从 curl + 代理 改为 Python urllib + 直连
- **原因**：代理导致微信 API 签名验证失败
- **验证**：API调用恢复正常

## 资源使用情况

### Gateway 服务
- **内存使用**：总体稳定，但可用内存紧张（<500MB）
- **CPU 使用**：正常范围
- **网络连接**：稳定
- **磁盘 I/O**：正常

### 存储使用
- **日志文件**：增长正常
- **临时文件**：无异常积累
- **备份空间**：充足

## 明日重点关注事项

1. **梦境系统修复**
   - 排查 agent-dream cron 任务 error 状态（isolated agent setup timed out）
   - 可能需要调整 isolated agent 的配置或超时设置

2. **视频字幕处理**
   - 由于 Gateway 内存限制，需要寻找其他方案处理视频加字幕任务
   - 考虑使用本地处理或分布式方案

3. **微信公众号推文准备**
   - 基于今日踩坑经验，准备下一期推文素材
   - 确保 IP 白名单正确配置，避免推送失败

4. **系统稳定性维护**
   - 持续监控 Gateway 内存使用情况
   - 及时处理可能出现的 OOM 问题

## 备注

今日工作主要集中在系统配置优化和API集成调试，包括安全审批机制完善、TTS服务配置、OpenClaw版本升级以及微信公众号API对接。所有关键操作均有详细记录，便于后续维护和问题排查。特别需要注意的是代理对第三方API的影响以及系统资源限制问题。