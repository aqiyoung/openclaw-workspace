#!/bin/bash
# Gmail INBOX bulk-cleanup loop.
# Paginates in:inbox, batches thread.modify with retries, sends Telegram progress.

set -u
# Don't `set -e` — we want to capture failures, not abort.

WORKDIR="/home/liyang/.openclaw/workspace/.gmail-cleanup"
GOGP="$WORKDIR/gogp.sh"
PROGRESS_LOG="$WORKDIR/progress.log"
INBOX_COUNTS_LOG="$WORKDIR/inbox-counts.log"
FAILED_IDS="$WORKDIR/failed-ids.txt"
SENT_IDS="$WORKDIR/sent-ids.txt"
PAGE_SIZE=100
PARALLEL=8
PROGRESS_EVERY=200
CHAT_ID="460212872"
MAX_PAGES=2000  # safety: 2000 * 100 = 200k threads cap

cd "$WORKDIR" || exit 1

# Make these available to xargs-invoked bash subprocesses
export WORKDIR GOGP

log() {
  printf '[%s] %s\n' "$(date -Iseconds)" "$*" | tee -a "$PROGRESS_LOG"
}

send_tg() {
  local body="$1"
  # send via openclaw message; ignore failures (don't kill the loop on Telegram issues)
  openclaw message send --channel telegram --target "$CHAT_ID" --message "$body" >/dev/null 2>>"$WORKDIR/telegram.err" || \
    log "telegram send failed: $body"
}

# gog search wrapper. Pages of 100, raw JSON.
fetch_page() {
  local token="$1"
  local out="$2"
  if [[ -z "$token" ]]; then
    "$GOGP" -j gmail search 'in:inbox' --max "$PAGE_SIZE" > "$out" 2>"$WORKDIR/gog.err"
  else
    "$GOGP" -j gmail search 'in:inbox' --max "$PAGE_SIZE" --page "$token" > "$out" 2>"$WORKDIR/gog.err"
  fi
}

# Modify one thread id, with up to 3 retries (so 4 total attempts).
# Returns 0 on success, 1 on permanent failure.
modify_thread() {
  local id="$1"
  local attempt
  for attempt in 1 2 3 4; do
    if "$GOGP" -j gmail thread modify "$id" \
         --add TRASH --remove "INBOX,UNREAD" \
         --no-input --force >/dev/null 2>>"$WORKDIR/gog.err"; then
      return 0
    fi
    sleep $((attempt * 2))  # backoff 2s,4s,6s,8s
  done
  return 1
}

export -f modify_thread
export GOGP
export WORKDIR

total_modified=0
total_failed=0
total_skipped_dup=0
page_num=0
token=""
empty_pages=0

log "===== Gmail INBOX cleanup start (page_size=$PAGE_SIZE parallel=$PARALLEL) ====="

while (( page_num < MAX_PAGES )); do
  page_num=$((page_num + 1))
  page_json="$WORKDIR/.page-$page_num.json"
  ids_file="$WORKDIR/.ids-$page_num.txt"

  if ! fetch_page "$token" "$page_json"; then
    log "page $page_num: fetch FAILED (network); backing off 15s"
    sleep 15
    # don't advance page_num on fetch failure — we want to retry this page
    page_num=$((page_num - 1))
    continue
  fi

  # Extract ids and token
  if ! jq -e '.threads' "$page_json" >/dev/null 2>&1; then
    log "page $page_num: fetch returned no .threads; raw:"
    head -c 500 "$page_json" | tee -a "$PROGRESS_LOG"
    log "backing off 30s and retrying"
    sleep 30
    page_num=$((page_num - 1))
    continue
  fi

  mapfile -t page_ids < <(jq -r '.threads[].id' "$page_json")
  new_token=$(jq -r '.nextPageToken // ""' "$page_json")
  count=${#page_ids[@]}

  printf '%s\n' "${page_ids[@]}" > "$ids_file"

  if (( count == 0 )); then
    empty_pages=$((empty_pages + 1))
    log "page $page_num: 0 threads (empty_pages=$empty_pages) — DONE"
    break
  fi

  log "page $page_num: got $count thread ids (token=${token:0:12}… → ${new_token:0:12}…)"

  # De-dup against already-sent-ids: skip ones we already trashed (resumability).
  if [[ -s "$SENT_IDS" ]]; then
    sort -u "$SENT_IDS" > "$WORKDIR/.sent.sorted"
    comm -23 <(sort -u "$ids_file") "$WORKDIR/.sent.sorted" > "$WORKDIR/.ids-$page_num.filt.txt"
    mv "$WORKDIR/.ids-$page_num.filt.txt" "$ids_file"
    new_count=$(wc -l < "$ids_file")
    skipped=$((count - new_count))
    if (( skipped > 0 )); then
      log "  de-dup: skipped $skipped already-processed ids"
      total_skipped_dup=$((total_skipped_dup + skipped))
      count=$new_count
    fi
  fi

  if (( count == 0 )); then
    log "  all ids in this page already processed; advancing"
    token="$new_token"
    [[ -z "$token" ]] && break
    continue
  fi

  # Parallel modify with retries, capturing per-id results.
  # We use a small wrapper that logs success/failure to a per-page result file.
  results_file="$WORKDIR/.results-$page_num.txt"
  : > "$results_file"
  export results_file
  xargs -P "$PARALLEL" -L 1 -a "$ids_file" bash -c '
    if modify_thread "$1"; then
      printf "ok\t%s\n" "$1" >> "$results_file"
    else
      printf "fail\t%s\n" "$1" >> "$results_file"
    fi
  ' _

  page_ok=$(grep -c "^ok" "$results_file" 2>/dev/null || echo 0)
  page_fail=$(grep -c "^fail" "$results_file" 2>/dev/null || echo 0)
  total_modified=$((total_modified + page_ok))
  total_failed=$((total_failed + page_fail))

  # Persist successful ids to SENT_IDS (for resumable skip next time)
  grep "^ok" "$results_file" | cut -f2 >> "$SENT_IDS"
  sort -u "$SENT_IDS" -o "$SENT_IDS"

  # Persist failed ids
  grep "^fail" "$results_file" | cut -f2 >> "$FAILED_IDS"
  sort -u "$FAILED_IDS" -o "$FAILED_IDS"

  # Track rough inbox size
  echo "$(date -Iseconds) after_page=$page_num modified_so_far=$total_modified failed_so_far=$total_failed" >> "$INBOX_COUNTS_LOG"

  log "page $page_num: ok=$page_ok fail=$page_fail  (running total: modified=$total_modified failed=$total_failed dup_skipped=$total_skipped_dup)"

  # Telegram progress every PROGRESS_EVERY cumulative modifications
  if (( total_modified / PROGRESS_EVERY > (total_modified - page_ok) / PROGRESS_EVERY )); then
    send_tg "🧹 Gmail INBOX cleanup: ${total_modified} trashed, ${total_failed} failed, ${total_skipped_dup} dup-skipped (page ${page_num})"
  fi

  token="$new_token"
  if [[ -z "$token" && $count -lt $PAGE_SIZE ]]; then
    log "page $page_num: last page (no next token, $count < $PAGE_SIZE) — DONE"
    break
  fi
  if [[ -z "$token" ]]; then
    # Got a full page with no token — Gmail sometimes does this when the rest
    # is small. Do a one-shot sanity fetch to confirm.
    log "page $page_num: full page with no next token — sanity fetch"
    "$GOGP" -j gmail search 'in:inbox' --max 100 > "$WORKDIR/.sanity.json" 2>>"$WORKDIR/gog.err"
    sanity_n=$(jq '.threads | length' "$WORKDIR/.sanity.json" 2>/dev/null || echo 0)
    log "sanity: $sanity_n threads remain in inbox (will be picked up next page if > 0)"
    if (( sanity_n == 0 )); then
      log "sanity: 0 threads — DONE"
      break
    fi
    # leave token="" to fetch the remaining; SENT_IDS dedup avoids re-processing
  fi
done

# Sanity: one more fetch to confirm zero
log "sanity check: one more in:inbox fetch…"
"$GOGP" -j gmail search 'in:inbox' --max 100 > "$WORKDIR/.final.json" 2>>"$WORKDIR/gog.err"
final_count=$(jq '.threads | length' "$WORKDIR/.final.json" 2>/dev/null || echo "err")
log "final sanity count: $final_count"

elapsed_secs=$(( $(date +%s) - $(date -d "$(head -1 "$PROGRESS_LOG" | cut -d' ' -f1 | tr -d '[]')" +%s 2>/dev/null || date +%s) ))
# Easier: just compute from process start
elapsed_secs=$SECONDS

log "===== DONE: modified=$total_modified failed=$total_failed dup_skipped=$total_skipped_dup pages=$page_num ====="

send_tg "✅ Gmail INBOX cleanup done. trashed=${total_modified} failed=${total_failed} dup_skipped=${total_skipped_dup} pages=${page_num} elapsed=${elapsed_secs}s"

# Persist summary for the card completion
cat > "$WORKDIR/summary.txt" <<EOF
modified=$total_modified
failed=$total_failed
dup_skipped=$total_skipped_dup
pages=$page_num
elapsed_secs=$elapsed_secs
final_inbox_count=$final_count
EOF
cat "$WORKDIR/summary.txt"
