#!/bin/bash
# Monitor: tracks /tmp/gmail_cleanup/ driver.
# When the driver is gone AND in:inbox is empty, writes summary and exits.
# This is just an observer — the agent (me) heartbeats the card.

set -u

WORKDIR="/home/liyang/.openclaw/workspace/.gmail-cleanup"
DRIVER_PID_FILE="/tmp/gmail_cleanup/driver.pid"
TOT_OK="/tmp/gmail_cleanup/total_ok.txt"
TOT_FAIL="/tmp/gmail_cleanup/total_fail.txt"
SEEN="/tmp/gmail_cleanup/seen_ids.txt"
TG_CHAT="460212872"
GOGP="$WORKDIR/gogp.sh"
MONITOR_LOG="$WORKDIR/monitor.log"

# Force a clean PATH and proxy for subcommands
export PATH="/home/liyang/.local/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
export HTTP_PROXY="http://127.0.0.1:7890"
export HTTPS_PROXY="http://127.0.0.1:7890"
export http_proxy="http://127.0.0.1:7890"
export https_proxy="http://127.0.0.1:7890"
export NO_PROXY="localhost,127.0.0.1,::1"

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*" | tee -a "$MONITOR_LOG"
}

send_tg() {
  openclaw message send --channel telegram --target "$TG_CHAT" --message "$1" >/dev/null 2>>"$WORKDIR/telegram.err" || \
    log "telegram send failed: $1"
}

log "===== monitor (v2) start ====="

last_status_ts=0
first_run=1
last_reported_ok=0

while true; do
  DRIVER_PID=$(cat "$DRIVER_PID_FILE" 2>/dev/null || echo "")
  if [[ -z "$DRIVER_PID" ]] || ! kill -0 "$DRIVER_PID" 2>/dev/null; then
    log "driver gone (pid='$DRIVER_PID') — verifying INBOX state"
    sleep 5
    final_count=$("$GOGP" -j gmail search 'in:inbox' --max 100 2>/dev/null | jq '.threads | length' 2>/dev/null || echo "err")
    log "post-driver in:inbox sample: $final_count"
    # If driver died but INBOX is non-zero, the user/orchestrator will likely restart it.
    # Wait 60s and re-check to handle restart race.
    sleep 60
    NEW_DRIVER_PID=$(cat "$DRIVER_PID_FILE" 2>/dev/null || echo "")
    if [[ -n "$NEW_DRIVER_PID" ]] && kill -0 "$NEW_DRIVER_PID" 2>/dev/null && [[ "$NEW_DRIVER_PID" != "$DRIVER_PID" ]]; then
      log "driver restarted ($DRIVER_PID → $NEW_DRIVER_PID) — resuming watch"
      continue
    fi
    break
  fi

  cur_ok=$(cat "$TOT_OK" 2>/dev/null || echo 0)
  cur_fail=$(cat "$TOT_FAIL" 2>/dev/null || echo 0)
  cur_seen=$(wc -l < "$SEEN" 2>/dev/null || echo 0)
  now=$(date +%s)

  if (( first_run )); then
    log "first status: driver pid=$DRIVER_PID ok=$cur_ok fail=$cur_fail seen=$cur_seen"
    first_run=0
  fi

  if (( now - last_status_ts >= 300 )); then
    log "status: driver alive (pid=$DRIVER_PID), ok=$cur_ok fail=$cur_fail seen=$cur_seen"
    last_status_ts=$now
  fi

  sleep 30
done

# Final state
final_ok=$(cat "$TOT_OK" 2>/dev/null || echo 0)
final_fail=$(cat "$TOT_FAIL" 2>/dev/null || echo 0)
final_seen=$(wc -l < "$SEEN" 2>/dev/null || echo 0)
final_inbox=$final_count

elapsed_min=$(( ( $(date +%s) - $(date -d "$(head -1 /tmp/gmail_cleanup/driver.stdout | cut -d']' -f1 | tr -d '[')" +%s 2>/dev/null || echo $(date +%s) ) ) / 60 ))

log "===== monitor end: ok=$final_ok fail=$final_fail seen=$final_seen in_inbox=$final_inbox elapsed_min=$elapsed_min ====="
send_tg "✅ Gmail INBOX cleanup driver finished. trashed=$final_ok failed=$final_fail seen=$final_seen in_inbox_after=$final_inbox elapsed=${elapsed_min}min"

cat > "$WORKDIR/summary.txt" <<EOF
ok=$final_ok
fail=$final_fail
seen=$final_seen
in_inbox_after=$final_inbox
elapsed_min=$elapsed_min
delegated_to=/tmp/gmail_cleanup/
EOF
log "summary saved to $WORKDIR/summary.txt"
