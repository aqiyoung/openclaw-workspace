# Infrastructure Management

## NAS Environment
- **Server**: threelnas (192.168.31.58)
- **Docker**: /usr/bin/docker
- **User Access**: Requires docker group membership
- **Containers**: 6 running normally

## Network & Proxy
- **Mihomo Proxy**: 127.0.0.1:7890
- **Docker Hub Issue**: TLS MITM by proxy causes certificate mismatch
- **Solutions**:
  1. Local `docker build` instead of pull
  2. Modify mihomo config to exclude Docker Hub domains

## Monitoring
- **NAS Events**: Local Python script (`scripts/nas_telegram_monitor.py`)
- **Service**: systemd service with Restart=always
- **Log**: `/vol1/1000/FNMessageBots/data/cursor/monitor.log`
- **Database**: `/usr/trim/var/eventlogger_service/logger_data.db3`

## Systemd Services
- **openclaw-restart-notify**: Gateway restart detection (every 15s)
- **nas-telegram-monitor**: Event monitoring daemon

## Critical Constraints
- **NO MODIFICATIONS**: `/usr/trim/` directory contents
- **Backup First**: Always backup before configuration changes
- **Proxy Bypass**: Unset HTTP_PROXY/HTTPS_PROXY for Cloudflare operations