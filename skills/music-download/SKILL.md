---
name: music-download
description: 全网音乐下载工具，默认优先高音质（320kbps/无损）。支持网易云音乐、QQ音乐、酷狗音乐、酷我音乐、咪咕音乐、YouTube、SoundCloud、Bilibili。当用户说"下载音乐"、"下载歌曲"、"搜歌"、"找歌"、"下歌"、"下载mp3"、"高音质"时使用此技能。
---

# Music Download · 全网音乐下载

## 核心原则：优先高音质

**默认目标是 320kbps 或更高音质**，不要用 YouTube（通常只有 128-143k opus，音质差）。

音质优先级：
1. **网易云 / 酷狗** — 通常 320kbps MP3（首选）
2. **QQ音乐 / 咪咕** — 可能更高或无损
3. **YouTube / SoundCloud** — 音质最差（兜底，仅当国内平台搜不到时）

## 调用流程

### 1. 搜索 → 只输出序号列表

先用国内平台搜（能拿到高音质）：

```bash
cd ~/.openclaw/workspace/skills/music-download/scripts && python3 musicdl.py search "关键词"
```

**只输出歌名 + 时长 + 平台，不要输出其他内容。** 格式：

```
1. 听风捎来旧时瑶 — 陆锦舟（2:49）网易云
2. 听风捎来旧时瑶 — 于牧野（3:48）网易云
3. 听风捎来旧时瑶 — 窝窝（3:17）酷狗
```

等用户回复序号。

### 2. 下载 → 高音质优先

**优先用 musicdl 从网易云/酷狗下载（320kbps）**，不要首选 yt-dlp：

```bash
# 方案A：musicdl 自动下载网易云前3首（320kbps）
cd ~/.openclaw/workspace/skills/music-download/scripts && python3 musicdl.py search "歌手 歌名" -s netease -l 5 -a -o /vol1/1000/music/
# 也可换 -s kugou（酷狗）对比哪个音质好
```

如果用户指定序号，或 musicdl 下载失败，再用 yt-dlp 兜底：

```bash
yt-dlp "ytsearch1:歌手 歌名" \
  -f "bestaudio[ext=m4a]/bestaudio" \
  --audio-format mp3 --audio-quality 0 \
  -o "/vol1/1000/music/%(title)s.%(ext)s" \
  --no-playlist
```

### 3. 验证音质 + 输出路径

下载后检查 bitrate，确认确实高音质：

```bash
for f in /vol1/1000/music/*关键词*.mp3; do
  echo "$f: $(stat -c%s "$f") bytes"
done
# 320kbps 参考：3分钟歌曲约 7MB / 4分钟约 9MB
```

只输出文件路径（含音质标注）：

```
✅ /vol1/1000/music/于牧野-听风捎来旧时瑶.mp3（320kbps）
```

**不要上传 NAS，不要发链接，不要发文件。用户要下载自己从 NAS 取。**

## 下载目录

`/vol1/1000/music/`

## 注意事项

- 搜索只输出序号列表，不要多余内容
- **高音质优先**：先用 musicdl 从网易云/酷狗拿 320kbps，yt-dlp 只兜底
- 网易云 `-a` 自动下载前 3 首，可对比哪个版本音质最好
- 若用户明确要"高音质/无损"，优先尝试网易云/咪咕（可能有无损）
- 下载完成后验证文件大小（320kbps ≈ 3分钟/7MB），太小的说明音质差
- 文件名中文无所谓，用户自己取