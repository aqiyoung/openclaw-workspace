# HEARTBEAT.md

## 审计通知检查
检查 `~/.openclaw/audit/pending_notification.txt` 是否存在。如果存在：
1. 读取内容
2. 通过当前通道发送给老板
3. 删除该文件
4. 回复 HEARTBEAT_OK

## 定时器健康检查
每 10 次心跳检查一次以下定时器是否正常运行：
- smart-home-monitor.timer
- nas-monitor.timer  
- openclaw-restart-notify.timer

用 `systemctl --user list-timers` 检查。如果发现丢失，立即重建并通知老板。
