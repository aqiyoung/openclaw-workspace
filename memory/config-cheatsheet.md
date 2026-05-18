# Configuration Cheat Sheet

## Model ID Rules
- **OpenClaw 配置**: 使用裸模型名（不带 provider 前缀）
  - `LongCat-2.0-Preview`
  - `LongCat-Flash-Lite`
  - `LongCat-Flash-Chat`
- **cron.json**: 同样使用裸模型名
- **错误示例**: `longcat/LongCat-Flash-Lite`（带前缀会失效）

## Delivery Format
- **统一格式**: `telegram:460212872`
- **用途**: 所有定时任务推送目标
- **优势**: 标准化、易维护

## Channels Configuration
```yaml
channels:
  telegram:
    enabled: true
```
- **位置**: content agent 配置中
- **作用**: 启用 Telegram 通道支持

## Docker Access
- **NAS 地址**: threelnas (192.168.31.58)
- **Docker 路径**: /usr/bin/docker
- **权限要求**: 用户需加入 docker 组
- **命令**: `usermod -aG docker $USER`

## Backup Strategy
- **备份目录**: `/vol1/1000/openclaw/backup/`
- **备份时机**: 每次重要变更后立即执行
- **配置备份**: 修改前复制原文件

## Cron Task Management
- **配置文件**: `~/.openclaw/cron/jobs.json`
- **重启通知**: Gateway 重启成功后必须推送"Gateway 重启成功 🍋"
- **监控**: systemd timer + bash 脚本（零 token 消耗）