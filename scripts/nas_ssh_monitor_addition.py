def init_ssh_cursor():
    """初始化 SSH journal cursor"""
    try:
        if os.path.exists(SSH_LOG_FILE):
            with open(SSH_LOG_FILE, 'r') as f:
                cursor = f.read().strip()
                if cursor:
                    return cursor
    except Exception as e:
        logger.warning(f"读取 SSH cursor 失败: {e}")
    try:
        import subprocess
        result = subprocess.run(
            ["journalctl", "-u", "sshd", "-n", "1", "-q", "--no-pager", "-o", "json"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            entry = json.loads(result.stdout.strip())
            cursor = entry.get("__CURSOR", "")
            if cursor:
                save_ssh_cursor(cursor)
                return cursor
    except Exception as e:
        logger.warning(f"初始化 SSH cursor 失败: {e}")
    return ""


def save_ssh_cursor(cursor):
    """保存 SSH journal cursor"""
    try:
        with open(SSH_LOG_FILE, 'w') as f:
            f.write(cursor)
    except Exception as e:
        logger.error(f"保存 SSH cursor 失败: {e}")


def check_ssh_log(last_cursor):
    """检查 SSH 登录日志（通过 journal）"""
    try:
        import subprocess

        cmd = ["journalctl", "-u", "sshd", "-q", "--no-pager", "-o", "json"]
        if last_cursor:
            cmd.append(f"--after-cursor={last_cursor}")
        else:
            cmd.extend(["-n", "1"])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return last_cursor

        lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
        if not lines:
            return last_cursor

        latest_cursor = last_cursor

        for line in lines:
            try:
                entry = json.loads(line)
                msg = entry.get("MESSAGE", "")
                cursor = entry.get("__CURSOR", "")
                timestamp = entry.get("__REALTIME_TIMESTAMP", "")

                if cursor:
                    latest_cursor = cursor

                if timestamp:
                    ts = int(timestamp) / 1_000_000
                    dt = datetime.fromtimestamp(ts, tz=timezone(timedelta(hours=8)))
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    time_str = "未知时间"

                ssh_event = None

                accepted_match = re.search(
                    r'Accepted (\w+) for (\S+) from (\S+) port (\d+)', msg
                )
                if accepted_match:
                    method, user, ip, port = accepted_match.groups()
                    ssh_event = {
                        "name": "✅ SSH 登录成功",
                        "user": user, "ip": ip,
                        "port": port, "method": method,
                        "time": time_str
                    }

                failed_match = re.search(
                    r'Failed (\w+) for (?:invalid user )?(\S+) from (\S+) port (\d+)', msg
                )
                if failed_match and not ssh_event:
                    method, user, ip, port = failed_match.groups()
                    ssh_event = {
                        "name": "❌ SSH 登录失败",
                        "user": user, "ip": ip,
                        "port": port, "method": method,
                        "time": time_str
                    }

                if ssh_event:
                    message_text = f"<b>飞牛NAS · {ssh_event['name']}</b>\n"
                    message_text += f"⏰ {ssh_event['time']}\n"
                    message_text += f"👤 {ssh_event['user']}\n"
                    message_text += f"🌐 {ssh_event['ip']}:{ssh_event['port']}\n"

                    if send_telegram_message(message_text):
                        logger.info(f"✅ 已发送 SSH 事件: {ssh_event['name']}")
                    else:
                        logger.error(f"❌ 发送 SSH 事件失败")

                    time.sleep(0.5)

            except Exception as e:
                logger.warning(f"解析 SSH 日志行失败: {e}")
                continue

        if latest_cursor and latest_cursor != last_cursor:
            save_ssh_cursor(latest_cursor)

        return latest_cursor

    except Exception as e:
        logger.error(f"SSH 日志检查失败: {e}")
        return last_cursor

