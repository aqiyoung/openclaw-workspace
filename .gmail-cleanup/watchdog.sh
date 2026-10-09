#!/bin/bash
# Watchdog: keeps the gmail cleanup driver alive.
# If driver.sh dies, wait 30s and restart it. Repeat indefinitely.
# Only exits cleanly when driver has been done for 5+ minutes (in:inbox actually empty).

set -u

WORKDIR="/tmp/gmail_cleanup"
DRIVER="$WORKDIR/driver.sh"
DRIVER_PID_FILE="$WORKDIR/driver.pid"
DRIVER_STDOUT="$WORKDIR/driver-resume3.stdout"
WATCHDOG_LOG="/home/liyang/.openclaw/workspace/.gmail-cleanup/watchdog.log"
TG_CHAT="460212872"

export PATH="/home/liyang/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1,::1"

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*" | tee -a "$WATCHDOG_LOG"
}

send_tg() {
  openclaw message send --channel telegram --target "$TG_CHAT" --message "$1" >/dev/null 2>>"$WORKDIR/telegram.err" || \
    log "telegram send failed: $1"
}

is_driver_alive() {
  local pid
  pid=$(cat "$DRIVER_PID_FILE" 2>/dev/null || echo "")
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    return 0
  fi
  return 1
}

start_driver() {
  cd "$WORKDIR" || exit 1
  setsid nohup bash "$DRIVER" > "$DRIVER_STDOUT" 2>&1 < /dev/null &
  local pid=$!
  echo "$pid" > "$DRIVER_PID_FILE"
  disown
  log "started driver pid=$pid"
  send_tg "🔄 Watchdog: restarted driver (pid=$pid) after previous run died"
  sleep 5
}

# Main loop
log "===== watchdog start ====="
send_tg "🛡️ Watchdog started: will auto-restart driver if it dies (handles the timeout 30 false-positive bug)"

restart_count=0
last_alive_ts=$(date +%s)

while true; do
  if is_driver_alive; then
    last_alive_ts=$(date +%s)
    sleep 30
    continue
  fi

  # Driver is dead
  now=$(date +%s)
  dead_for=$((now - last_alive_ts))
  log "driver dead (was alive at $last_alive_ts, dead for ${dead_for}s)"

  # Check if driver actually completed (in:inbox sample returns 0 for 3 consecutive checks)
  # This is a sanity check — the driver.sh now has the bugfix, so it won't falsely conclude done
  final_count=0
  for i in 1 2 3; do
    cf=$(mktemp)
    timeout 30 gog gmail search "in:inbox" --max=10 --plain > "$cf" 2>&1
    if grep -q "^ID" "$cf" 2>/dev/null; then
      n=$(awk -F'\t' 'NR>1 && $1!="" {c++} END {print c+0}' "$cf")
      log "sanity check $i: in:inbox sampled 10 returned $n"
      if [ "$n" = "0" ]; then
        final_count=$((final_count + 1))
      else
        final_count=0
        break
      fi
    else
      log "sanity check $i: inconclusive (timeout/error)"
      final_count=0
      break
    fi
    rm -f "$cf"
  done

  if [ "$final_count" -ge 3 ]; then
    log "driver truly done (3 consecutive empty samples). Exiting watchdog."
    send_tg "✅ Watchdog: driver truly done (in:inbox empty for 3 consecutive checks). Watchdog exiting."
    break
  fi

  # Restart driver
  restart_count=$((restart_count + 1))
  log "restarting driver (attempt $restart_count)"
  start_driver
  last_alive_ts=$(date +%s)
  sleep 10
done

log "===== watchdog end ====="
