# 网络安全技能库 (Anthropic Cybersecurity Skills)

## 概述
754 个生产级网络安全技能，覆盖 26 个安全领域，遵循 agentskills.io 标准。

## 位置
`~/.openclaw/workspace/Anthropic-Cybersecurity-Skills/`

## 使用方式
当需要安全相关任务时，AI 会自动参考对应技能。以下是常用场景：

## 常用技能速查

### 代码安全审计
- `skills/performing-code-review-for-security-vulnerabilities/`
- `skills/detecting-sql-injection/`
- `skills/detecting-xss-vulnerabilities/`
- `skills/analyzing-api-security/`

### 渗透测试
- `skills/conducting-network-penetration-testing/`
- `skills/conducting-web-application-penetration-testing/`
- `skills/conducting-cloud-penetration-testing/`

### 漏洞扫描
- `skills/scanning-for-vulnerabilities-with-nessus/`
- `skills/performing-vulnerability-assessment/`

### 应急响应
- `skills/responding-to-ransomware-incident/`
- `skills/conducting-incident-response/`
- `skills/performing-memory-forensics-with-volatility3/`

### 云安全
- `skills/auditing-aws-security-configurations/`
- `skills/auditing-azure-security-configurations/`
- `skills/auditing-gcp-security-configurations/`

### 容器安全
- `skills/scanning-container-images-for-vulnerabilities/`
- `skills/auditing-kubernetes-rbac-configurations/`

### 日志分析
- `skills/analyzing-windows-event-logs/`
- `skills/analyzing-linux-authentication-logs/`
- `skills/analyzing-cloud-audit-logs/`

### 恶意软件分析
- `skills/analyzing-malware-with-sandbox/`
- `skills/performing-static-malware-analysis/`
- `skills/performing-dynamic-malware-analysis/`

## 使用示例

用户：帮我看看这段代码有没有 SQL 注入风险
AI：自动参考 `detecting-sql-injection` 技能，按专业流程检查

用户：分析这个内存 dump 有没有恶意软件
AI：自动参考 `performing-memory-forensics-with-volatility3` 技能

用户：检查我的 AWS 配置安全吗
AI：自动参考 `auditing-aws-security-configurations` 技能

## 技能结构
```
skills/<skill-name>/
├── SKILL.md          # 技能定义（YAML frontmatter + 工作流）
├── references/       # MITRE ATT&CK 等框架映射
├── scripts/          # 辅助脚本
└── assets/           # 模板和检查清单
```

## 框架映射
每个技能都映射到：
- MITRE ATT&CK（攻击技术）
- NIST CSF 2.0（安全框架）
- MITRE ATLAS（AI/ML 威胁）
- MITRE D3FEND（防御措施）
- NIST AI RMF（AI 风险管理）
