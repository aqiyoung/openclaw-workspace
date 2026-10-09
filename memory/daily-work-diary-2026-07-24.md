# 2026-07-24 周五 工作日记

## 1. 下午~傍晚 — Gateway 宕机 4 分钟，APP 断连

**事件**：18:29~18:33 Gateway 挂掉（nginx `Connection refused`），手机 Xiaomi 15 的 WebSocket 断开。19:37 重启 Gateway 恢复，但节点重新连接后依然不稳定。

## 2. 20:00 — 排查 APP 连不上的根因（Node webchat 会话）

**threely 反馈**：APP 重启、重置、重新安装后仍然连不上，怀疑最近改的 APP 代码有问题。

**排查过程**：
- 检查了 Gateway 日志，发现手机发来的 WebSocket 握手全部超时
- 关键日志：`cause: "handshake-timeout"`，`handshakeMs: 15000`，`phase: "ws_upgrade_started"`
- Gateway 的 event loop 延迟高达 15 秒（`eventLoopDelayMaxMs=14998.8`）
- CPU 跑到 65%+，内存 890MB

**结论**：不是 APP 代码问题，是 Gateway 负载太高，WebSocket 握手请求根本排不上队。

**threely 问 Gateway token**，确认了 token 配置（`0c272dab5a052a9701a9ed60fc8a178af7b797914e8d429345ac6a40c7e55a3e`），但 APP 连接用的是 WebSocket 节点配对，不走 token。

## 3. 23:16 — threely 在 Telegram 问 APP session 是否卡死

**处理**：发现 Xiaomi 15 的 session（`agent:main:node-bb1a860decea`）确实卡住了——最后一条消息 assistant 跑失败（error），然后 fallback 到 glm-5.2 才回复，之后一直挂在那没动过，status 标着 "running"。

**解决**：threely 说"清了"，执行了 session 清理，把那个卡住的 session 归档清掉，状态变为 `done`。节点还是 disconnected，需要 threely 重新打开 APP 重连。

## 主要成就

- 快速定位了 APP 连不上的真正原因（Gateway 负载过高导致 WebSocket 握手超时），排除了 APP 代码 bug 的嫌疑
- 清掉了卡死的 APP session

## 犯的错误

- 无

## 待办

- Gateway 负载问题未解决：只有 3.7G 内存，Gateway 吃 890M，mihomo 占 292M。需要优化或加内存，否则 WebSocket 握手超时会反复出现
- 检查是否有其他服务可以关掉释放资源