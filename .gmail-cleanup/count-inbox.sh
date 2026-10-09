#!/bin/bash
# Count INBOX items
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890

total=0
token=""
page=0
while [[ $page -lt 5 ]]; do
  page=$((page + 1))
  if [[ -z "$token" ]]; then
    /home/liyang/.openclaw/workspace/.gmail-cleanup/gogp.sh -j gmail search 'in:inbox' --max 100 > /tmp/count-p$page.json 2>/dev/null
  else
    /home/liyang/.openclaw/workspace/.gmail-cleanup/gogp.sh -j gmail search 'in:inbox' --max 100 --page "$token" > /tmp/count-p$page.json 2>/dev/null
  fi
  c=$(jq '.threads | length' /tmp/count-p$page.json 2>/dev/null || echo 0)
  token=$(jq -r '.nextPageToken // ""' /tmp/count-p$page.json 2>/dev/null)
  total=$((total + c))
  echo "page $page: +$c (running $total) token=${token:0:12}…"
  if [[ -z "$token" && $c -lt 100 ]]; then
    echo "DONE: $total total"
    break
  fi
  if [[ -z "$token" ]]; then
    echo "no token but full page; need one more"
    break
  fi
done
echo "---"
echo "total: $total in $page pages"
