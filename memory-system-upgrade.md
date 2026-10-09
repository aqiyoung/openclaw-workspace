# Memory System Upgrade Plan

> 基于 Claude Code 源码设计模式，优化 OpenClaw 记忆系统
> 原则：只改 workspace 层，不动 OpenClaw 本体，不影响后续升级

## 一、智能记忆提取（extractMemories 模式）

### Claude Code 设计
- 每次对话结束，fork 子 agent 从对话中提取值得记住的事项
- 结构化存储（frontmatter + 内容）
- 四种类型：user / feedback / project / reference

### OpenClaw 实施方案
- **位置**：`skills/memory-extractor/`
- **触发**：心跳时（每次或每 N 次）
- **输出**：`memory/extracted/YYYY-MM-DD.md`（结构化）
- **去重**：先检查是否已存在相似记忆

### 实施步骤
1. [x] 创建 skill 目录结构
2. [ ] 实现 SKILL.md（核心逻辑）
3. [ ] 创建提取模板（frontmatter 格式）
4. [ ] 集成到 HEARTBEAT.md

---

## 二、相关记忆智能检索（findRelevantMemories 模式）

### Claude Code 设计
- 扫描记忆文件，提取 name + description
- 用 LLM 从清单中挑选 top 5 相关记忆
- 排除已使用的记忆（避免重复）

### OpenClaw 实施方案
- **位置**：`skills/memory-selector/`
- **输入**：当前对话 + 记忆清单
- **输出**：top 5 相关记忆路径
- **集成**：在 memory_recall 之前加一层过滤

### 实施步骤
1. [ ] 创建记忆清单扫描脚本
2. [ ] 实现相关性判断逻辑
3. [ ] 与现有 memory 系统对接

---

## 三、Token 预算管理（autoCompact 模式）

### Claude Code 设计
- 实时追踪 token 用量
- 多级阈值：警告(70%) / 提醒(80%) / 自动压缩(90%) / 阻断(95%)
- 在接近上限时自动压缩历史

### OpenClaw 实施方案
- **位置**：`scripts/context_budget.sh`
- **检查**：心跳时运行
- **输出**：写入 `/tmp/openclaw/context_budget.json`
- **告警**：超过阈值时推微信

### 实施步骤
1. [x] 已有 session_status 获取 token 信息
2. [ ] 创建预算检查脚本
3. [ ] 集成到 HEARTBEAT.md
4. [ ] 添加自动清理逻辑

---

## 四、微压缩（microCompact 模式）

### Claude Code 设计
- 不清空整段历史
- 选择性清理旧的工具调用结果
- 保留对话骨架（决策、结论）

### OpenClaw 实施方案
- **位置**：`scripts/memory_cleanup.sh`
- **规则**：
  - 天气数据：保留 7 天
  - 任务详情：完成后 3 天清理
  - 决策/偏好：永久保留
- **执行**：每天凌晨自动运行

### 实施步骤
1. [ ] 定义清理规则
2. [ ] 实现清理脚本
3. [ ] 添加到 systemd timer

---

## 五、多层级配置（CLAUDE.md 模式）

### Claude Code 设计
- 项目级 → 用户级 → 系统级
- 上级覆盖下级

### OpenClaw 实施方案
- **已有**：`AGENTS.md` + `SOUL.md` + `MEMORY.md`
- **新增**：`~/.openclaw/global-rules.md`（全局层）
- **优先级**：workspace > global > system

### 实施步骤
1. [ ] 创建 global-rules.md 模板
2. [ ] 定义优先级规则
3. [ ] 更新 AGENTS.md 说明

---

## 当前进度

- [x] 规划文档创建（2026-04-02 23:06）
- [ ] 智能记忆提取（待实施）
- [ ] 相关记忆检索（待实施）
- [ ] Token 预算管理（待实施）
- [ ] 微压缩清理（待实施）
- [ ] 多层级配置（待实施）

---

## 文件清单

### 新增文件
- `skills/memory-extractor/SKILL.md`
- `skills/memory-selector/SKILL.md`
- `scripts/context_budget.sh`
- `scripts/memory_cleanup.sh`
- `~/.openclaw/global-rules.md`

### 修改文件
- `HEARTBEAT.md`（集成新检查项）
- `AGENTS.md`（添加多层级说明）

---

*最后更新：2026-04-02 23:06*
