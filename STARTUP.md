# STARTUP.md - Session Startup Optimization

每次会话启动时，按以下阶段加载上下文：

## Phase 1 — 身份（必须，立即加载）

**目的**：知道我是谁，服务谁

加载文件：
- `IDENTITY.md` — 我的身份（名字、性格、emoji）
- `USER.md` — 用户信息（名字、偏好、时区）

**估算**：~2K tokens

## Phase 2 — 上下文（主会话必须，子会话跳过）

**目的**：恢复长期记忆

**仅主会话**加载：
- `MEMORY.md` — 长期记忆（重要事件、偏好、规则）

**子会话**跳过此阶段（避免泄露用户隐私）

**估算**：~15K tokens

## Phase 3 — 今日上下文（必须，快速）

**目的**：了解最近发生的事

加载文件：
- `memory/YYYY-MM-DD.md` — 今日笔记
- `memory/YYYY-MM-DD.md`（昨天） — 昨日笔记

如果文件不存在，跳过。

**估算**：~3K tokens

## Phase 4 — 技能描述（按需，延迟）

**目的**：知道有什么工具可用

**不加载完整 SKILL.md**，只扫描 `skills/*/SKILL.md` 的前 10 行（description 部分）

匹配规则：
- 如果用户消息明确提到某个 skill 的关键词 → 加载完整 SKILL.md
- 否则 → 只加载描述，保持轻量

**估算**：~2K tokens（描述模式）

## Phase 5 — 自我改进检查（可选）

**目的**：持续改进

检查 `~/self-improving/memory.md` 是否有更新
- 如果有 → 加载并应用
- 如果没有 → 跳过

**估算**：~1K tokens

---

## Token 预算

| 阶段 | 主会话 | 子会话 |
|------|--------|--------|
| Phase 1 | 2K | 2K |
| Phase 2 | 15K | 0 |
| Phase 3 | 3K | 3K |
| Phase 4 | 2K | 2K |
| Phase 5 | 1K | 0 |
| **总计** | **23K** | **7K** |

---

## 实施方式

OpenClaw 的 Project Context 已经自动注入了 `IDENTITY.md`、`USER.md`、`MEMORY.md` 等文件。

**我需要做的优化**：
1. 在心跳时检查是否需要加载 Phase 3/4/5
2. 对于大 skill，延迟加载完整 SKILL.md
3. 记录 token 消耗，监控优化效果

---

_此文件仅供参考，OpenClaw 的 Project Context 机制已经处理了大部分加载逻辑。_
