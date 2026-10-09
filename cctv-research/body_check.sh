#!/bin/bash
URLS=(
  "http://74.91.26.218:82/live/cctv1hd.m3u8"
  "http://74.91.26.218:82/live/cctv3hd.m3u8"
  "http://74.91.26.218:82/live/cctv7hd.m3u8"
  "http://74.91.26.218:82/live/cctv13hd.m3u8"
  "http://74.91.26.218:82/live/cctv15hd.m3u8"
  "https://xykt-fix.github.io/play/a02b/index.m3u8"
  "https://dash2.antik.sk/live/test_cctv_tizen/playlist.m3u8"
  "http://198.204.240.250:82/live/cctv1.m3u8"
  "http://38.75.136.137:98/gslb/dsdqpub/fyzq.m3u8?auth=testpub"
  "https://cdn4.skygo.mn/live/disk1/CCTV-10/HLSv3-FTA/CCTV-10.m3u8"
)
for u in "${URLS[@]}"; do
    echo "=== $u ==="
    curl -sS -L --max-time 5 -r 0-512 -A "Mozilla/5.0" "$u" 2>&1 | head -20
    echo ""
done
