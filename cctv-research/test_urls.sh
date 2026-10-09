#!/bin/bash
# Test a URL: HEAD + 1KB GET, time the response
URL=$1
LABEL=${2:-$URL}
TIMEOUT=${3:-8}
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"

START=$(date +%s%N)
HEAD=$(curl -sS -o /dev/null -w "%{http_code}|%{size_download}|%{time_total}" \
    -A "$UA" \
    --max-time $TIMEOUT \
    -L \
    -X HEAD \
    "$URL" 2>&1)
HEAD_EXIT=$?
END=$(date +%s%N)
ELAPSED_MS=$(( (END - START) / 1000000 ))

# Try a range GET to verify body
GET=$(curl -sS -o /tmp/cctv_test_chunk.bin -w "%{http_code}|%{size_download}|%{time_total}" \
    -A "$UA" \
    --max-time $TIMEOUT \
    -L \
    -r 0-1023 \
    "$URL" 2>&1)
GET_EXIT=$?
BYTES=$(stat -c %s /tmp/cctv_test_chunk.bin 2>/dev/null || echo 0)
HEAD_BYTES=$(head -c 1024 /tmp/cctv_test_chunk.bin 2>/dev/null)

echo "[$LABEL]"
echo "  url=$URL"
echo "  HEAD=$HEAD exit=$HEAD_EXIT elapsed=${ELAPSED_MS}ms"
echo "  GET =$GET exit=$GET_EXIT bytes=$BYTES"
echo "  body_head=$(echo "$HEAD_BYTES" | head -c 200 | tr -d '\0')"
echo ""
