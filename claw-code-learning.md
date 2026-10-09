# claw-code 学习总结 — 功能进化规划

## 📚 学习来源
claw-code (原 instructkr/claw-code) — 2026-03-31 Claude Code 源码泄露事件后的重写项目

---

## 🎯 已创建的 Skills

| # | Skill | 功能 | 文件 |
|---|-------|------|------|
| 1 | cost_tracker | Token 消耗记录 | `~/.openclaw/cost_tracker/` |
| 2 | safe-spawn | 工具权限控制 | `skills/safe-spawn/SKILL.md` |
| 3 | skill-router | 技能路由优化 | `skills/skill-router/SKILL.md` |
| 4 | session-persist | 会话持久化 | `skills/session-persist/SKILL.md` |
| 5 | bootstrap-opt | 启动优化 | `skills/bootstrap-opt/SKILL.md` |
| 6 | stop-reason | 任务状态判断 | `skills/stop-reason/SKILL.md` |
| 7 | history-log | 执行历史记录 | `skills/history-log/SKILL.md` |

---

## 📊 功能对比

| 功能 | claw-code | OpenClaw 现状 | 我们的方案 |
|------|-----------|---------------|------------|
| turn-loop | ✅ `maxTurns` | ❌ 无 | 等 OpenClaw 支持 |
| cost_tracker | ✅ 内置 | ⚠️ 有基础 | cost_tracker skill |
| permissions | ✅ `deny_names` | ❌ 无 | safe-spawn 模拟 |
| routing | ✅ `_score()` | ⚠️ 简单匹配 | skill-router 优化 |
| transcript | ✅ 自动持久化 | ⚠️ 有 transcriptPath | session-persist 利用 |
| bootstrap | ✅ 分阶段 | ⚠️ 固定加载 | bootstrap-opt 指南 |
| stop_reason | ✅ 多种状态 | ⚠️ 只有 done/error | stop-reason 判断 |
| history | ✅ `HistoryLog` | ❌ 无 | history-log 记录 |

---

## 🚀 实施优先级

### P0 — 立即可用
- [x] cost_tracker — 已创建基础设施
- [x] STARTUP.md — 分阶段启动指南
- [ ] history-log — 需要在心跳中集成

### P1 — 近期实施
- [ ] safe-spawn — 测试权限模拟
- [ ] skill-router scoring — 配置评分规则
- [ ] stop-reason — 监控子 agent 状态

### P2 — 等 OpenClaw 官方
- [ ] maxTurns 参数
- [ ] sessions_persist/resume
- [ ] 工具权限控制参数

---

## 📁 文件结构

```
~/.openclaw/
├── cost_tracker/
│   ├── config.json # 模型费率配置
│   ├── cost_tracker.py # 记录逻辑
│   └── show_cost.py # 显示汇总
│
├── history/
│   └── YYYY-MM-DD.jsonl # 执行历史（待创建）
│
└── workspace/
    ├── STARTUP.md # 分阶段启动指南
    ├── HEARTBEAT.md # 已更新：增加 cost_tracker
    │
    └── skills/
        ├── safe-spawn/
        ├── skill-router/
        │   └── scoring.md
        ├── session-persist/
        ├── bootstrap-opt/
        ├── stop-reason/
        └── history-log/
```

---

## 🔮 后续工作

1. **测试 cost_tracker** — 下次心跳验证记录
2. **集成 history-log** — 在心跳中记录执行历史
3. **配置 skill-router** — 创建评分配置文件
4. **监控子 agent** — 利用 stop-reason 判断状态

---

_此文档记录 2026-04-02 的 claw-code 学习和功能进化规划。_
