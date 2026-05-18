#!/usr/bin/env python3
"""
musicdl - 全网音乐下载工具 v2.0
支持: 网易云音乐、QQ音乐、酷狗音乐、酷我音乐、咪咕音乐、YouTube、SoundCloud、Bilibili
"""

import os
import sys
import json
import time
import hashlib
import argparse
import subprocess
import re
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ 需要 requests: pip3 install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

try:
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

# ─── 配置 ────────────────────────────────────────────────────────────────────

DEFAULT_OUTPUT = "/vol1/1000/Music"
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/",
})

console = Console() if HAS_RICH else None

# 检查 yt-dlp 是否可用
def check_ytdlp():
    try:
        r = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except:
        return False

HAS_YTDLP = check_ytdlp()

def log(msg, style=None):
    if console and style:
        console.print(msg, style=style)
    else:
        print(msg)


# ─── 工具函数 ────────────────────────────────────────────────────────────────

def sanitize_filename(name):
    for c in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(c, '_')
    return name.strip()

def format_duration(ms):
    if not ms:
        return "--:--"
    s = int(ms / 1000)
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"

def download_file(url, filepath, desc="下载中"):
    """下载文件到本地"""
    try:
        resp = SESSION.get(url, stream=True, timeout=60)
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
        return True
    except Exception as e:
        log(f"  ❌ 下载失败: {e}", style="red")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False

def embed_id3_tags(filepath, title="", artist="", album="", cover_url=None):
    """写入 ID3 标签"""
    if not HAS_MUTAGEN:
        return
    try:
        if filepath.endswith('.mp3'):
            try:
                audio = MP3(filepath)
            except:
                return
            if audio.tags is None:
                audio.add_tags()
            if title:
                audio.tags["TIT2"] = TIT2(encoding=3, text=title)
            if artist:
                audio.tags["TPE1"] = TPE1(encoding=3, text=artist)
            if album:
                audio.tags["TALB"] = TALB(encoding=3, text=album)
            if cover_url:
                try:
                    cover_resp = SESSION.get(cover_url, timeout=10)
                    if cover_resp.status_code == 200:
                        audio.tags["APIC"] = APIC(
                            encoding=3, mime="image/jpeg", type=3,
                            desc="Cover", data=cover_resp.content
                        )
                except:
                    pass
            audio.save()
    except Exception:
        pass


# ─── 网易云音乐 ──────────────────────────────────────────────────────────────

class NeteaseMusicClient:
    """网易云音乐下载"""

    BASE_URL = "https://music.163.com"

    def search(self, keyword, limit=10):
        url = f"{self.BASE_URL}/api/search/get"
        params = {"s": keyword, "type": 1, "limit": limit, "offset": 0}
        try:
            resp = SESSION.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("result") and data["result"].get("songs"):
                songs = []
                for s in data["result"]["songs"][:limit]:
                    artists = "/".join(a["name"] for a in s.get("artists", []))
                    album = s.get("album", {}).get("name", "")
                    duration = s.get("duration", 0)
                    # 获取封面
                    cover = s.get("album", {}).get("picUrl", "")
                    songs.append({
                        "id": s["id"],
                        "name": s["name"],
                        "artists": artists,
                        "album": album,
                        "duration": duration,
                        "cover": cover,
                        "source": "netease",
                    })
                return songs
        except Exception as e:
            log(f"  ⚠️ 网易云搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, song_id):
        url = f"{self.BASE_URL}/api/song/enhance/player/url"
        params = {"ids": f"[{song_id}]", "br": 320000}
        try:
            resp = SESSION.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("data") and data["data"][0].get("url"):
                return data["data"][0]["url"]
        except Exception:
            pass
        return None


# ─── QQ音乐 ──────────────────────────────────────────────────────────────────

class QQMusicClient:
    """QQ音乐下载 (移动端 API)"""

    def search(self, keyword, limit=10):
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
        payload = {
            "music.search.SearchCgiService": {
                "module": "music.search.SearchCgiService",
                "method": "DoSearchForQQMusicDesktop",
                "param": {
                    "query": keyword,
                    "num_per_page": limit,
                    "page_num": 1,
                    "search_type": 0,
                }
            }
        }
        try:
            resp = SESSION.post(url, json=payload, headers={"Referer": "https://y.qq.com/"}, timeout=10)
            data = resp.json()
            body = data.get("music.search.SearchCgiService", {}).get("data", {}).get("body", {})
            song_list = body.get("song", {}).get("list", [])
            songs = []
            for s in song_list[:limit]:
                artists = "/".join(a["name"] for a in s.get("singer", []))
                album = s.get("album", {}).get("title", "")
                mid = s.get("mid", "")
                # 封面
                albummid = s.get("album", {}).get("mid", "")
                cover = f"http://y.gtimg.cn/music/photo_new/T002R300x300M000{albummid}.jpg" if albummid else ""
                songs.append({
                    "id": mid,
                    "name": s.get("name", ""),
                    "artists": artists,
                    "album": album,
                    "duration": s.get("interval", 0) * 1000,
                    "cover": cover,
                    "source": "qq",
                })
            return songs
        except Exception as e:
            log(f"  ⚠️ QQ音乐搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, song_mid):
        """获取 QQ 音乐播放 URL"""
        # 尝试多个音质
        for quality, prefix, ext in [("320", "M800", "mp3"), ("128", "M500", "mp3"), ("96", "C400", "m4a"), ("48", "C200", "m4a")]:
            try:
                url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
                filename = f"{prefix}{song_mid}.{ext}"
                payload = {
                    "req_0": {
                        "module": "vkey.GetVkeyServer",
                        "method": "CgiGetVkey",
                        "param": {
                            "guid": hashlib.md5(str(time.time()).encode()).hexdigest()[:10],
                            "songmid": [song_mid],
                            "songtype": [0],
                            "uin": "0",
                            "loginflag": 1,
                            "platform": "20",
                            "filename": [filename],
                            "code": 0,  # 0=免费
                        }
                    }
                }
                resp = SESSION.post(url, json=payload, headers={"Referer": "https://y.qq.com/"}, timeout=10)
                data = resp.json()
                sip = data.get("req_0", {}).get("data", {}).get("sip", [])
                midurlinfo = data.get("req_0", {}).get("data", {}).get("midurlinfo", [{}])
                if midurlinfo and midurlinfo[0].get("purl"):
                    base = sip[0] if sip else "http://ws.stream.qqmusic.qq.com/"
                    return f"{base}{midurlinfo[0]['purl']}"
                # 尝试 oplist
                oplist = midurlinfo[0].get("opist_url", "")
                if oplist:
                    return oplist
            except Exception:
                continue
        return None


# ─── 酷狗音乐 ────────────────────────────────────────────────────────────────

class KugouMusicClient:
    """酷狗音乐下载"""

    SEARCH_URL = "https://songsearch.kugou.com/song_search_v2"

    def search(self, keyword, limit=10):
        params = {
            "keyword": keyword, "page": 1, "pagesize": limit,
            "userid": -1, "clientver": "", "platform": "WebFilter",
            "filter": 2, "iscorrection": 1, "privilege_filter": 0,
        }
        try:
            resp = SESSION.get(self.SEARCH_URL, params=params, timeout=10)
            data = resp.json()
            songs = []
            for s in data.get("data", {}).get("lists", [])[:limit]:
                name = s.get("SongName", "").replace("<em>", "").replace("</em>", "")
                artists = s.get("SingerName", "").replace("<em>", "").replace("</em>", "")
                album = s.get("AlbumName", "")
                duration = s.get("Duration", 0) * 1000
                # 封面
                cover = s.get("Image", "").replace("{size}", "400") if s.get("Image") else ""
                songs.append({
                    "id": s.get("FileHash", ""),
                    "name": name,
                    "artists": artists,
                    "album": album,
                    "duration": duration,
                    "cover": cover,
                    "source": "kugou",
                })
            return songs
        except Exception as e:
            log(f"  ⚠️ 酷狗搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, file_hash):
        url = "https://wwwapi.kugou.com/yy/index.php"
        params = {"r": "play/getdata", "hash": file_hash}
        try:
            resp = SESSION.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("data") and data["data"].get("play_url"):
                return data["data"]["play_url"]
        except Exception:
            pass
        return None


# ─── 酷我音乐 ────────────────────────────────────────────────────────────────

class KuwoMusicClient:
    """酷我音乐下载"""

    SEARCH_URL = "https://www.kuwo.cn/api/www/search/searchMusicBykeyWord"

    def search(self, keyword, limit=10):
        try:
            # 先获取 cookie
            SESSION.get("https://www.kuwo.cn/", timeout=10)
            hm_iuvt = SESSION.cookies.get("Hm_Iuvt_cdb524f42f23cer9b268564v7y735ewrq2324", "")
            headers = {"Referer": "https://www.kuwo.cn/", "csrf": hm_iuvt}
            resp = SESSION.get(self.SEARCH_URL,
                             params={"key": keyword, "pn": 1, "rn": limit, "httpsStatus": 1},
                             headers=headers, timeout=10)
            data = resp.json()
            if data.get("success") == False:
                # 被拒绝，返回空
                return []
            songs = []
            for s in data.get("data", {}).get("list", [])[:limit]:
                songs.append({
                    "id": s.get("rid", ""),
                    "name": s.get("name", ""),
                    "artists": s.get("artist", ""),
                    "album": s.get("album", ""),
                    "duration": s.get("duration", 0) * 1000,
                    "cover": s.get("pic", ""),
                    "source": "kuwo",
                })
            return songs
        except Exception as e:
            log(f"  ⚠️ 酷我搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, rid):
        url = "https://www.kuwo.cn/api/v1/www/music/playUrl"
        params = {"mid": rid, "type": "music", "httpsStatus": 1}
        try:
            resp = SESSION.get(url, params=params, timeout=10)
            data = resp.json()
            if data.get("data") and data["data"].get("url"):
                return data["data"]["url"]
        except Exception:
            pass
        return None


# ─── 咪咕音乐 ────────────────────────────────────────────────────────────────

class MiguMusicClient:
    """咪咕音乐下载"""

    SEARCH_URL = "https://m.music.migu.cn/migumusic/h5/search/searchAll"

    def search(self, keyword, limit=10):
        try:
            # 咪咕需要特殊的 UA
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0",
                "Referer": "https://m.music.migu.cn/",
                "Origin": "https://m.music.migu.cn",
            }
            params = {"keyword": keyword, "type": 2, "pgc": 1, "rows": limit, "page": 1}
            resp = SESSION.get(self.SEARCH_URL, params=params, headers=headers, timeout=10)
            if resp.headers.get("content-type", "").startswith("application/json"):
                data = resp.json()
                songs = []
                for s in data.get("data", {}).get("songs", [])[:limit]:
                    artists = "/".join(a for a in s.get("singerName", []) if a)
                    songs.append({
                        "id": s.get("id", ""),
                        "name": s.get("name", ""),
                        "artists": artists,
                        "album": s.get("albumName", ""),
                        "duration": s.get("duration", 0),
                        "cover": s.get("imgItems", [{}])[0].get("img", "") if s.get("imgItems") else "",
                        "source": "migu",
                    })
                return songs
        except Exception as e:
            log(f"  ⚠️ 咪咕搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, song_id):
        url = "https://m.music.migu.cn/migumusic/h5/song/info"
        params = {"songId": song_id}
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://m.music.migu.cn/",
        }
        try:
            resp = SESSION.get(url, params=params, headers=headers, timeout=10)
            data = resp.json()
            if data.get("data") and data["data"].get("playUrl"):
                return data["data"]["playUrl"]
        except Exception:
            pass
        return None


# ─── YouTube (via yt-dlp) ───────────────────────────────────────────────────

class YouTubeClient:
    """YouTube 音乐下载 (via yt-dlp)"""

    def __init__(self):
        self.available = HAS_YTDLP

    def search(self, keyword, limit=10):
        if not self.available:
            return []
        try:
            result = subprocess.run(
                ["yt-dlp", "--no-download", "--print", "%(id)s|%(title)s|%(duration)s|%(uploader)s|%(view_count)s",
                 f"ytsearch{limit}:{keyword} music"],
                capture_output=True, text=True, timeout=30
            )
            songs = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 4)
                    if len(parts) >= 4:
                        song_id, title, duration, uploader = parts[0], parts[1], parts[2], parts[3]
                        try:
                            dur_sec = int(duration) * 1000 if duration.isdigit() else 0
                        except:
                            dur_sec = 0
                        songs.append({
                            "id": song_id,
                            "name": title,
                            "artists": uploader,
                            "album": "",
                            "duration": dur_sec,
                            "cover": f"https://i.ytimg.com/vi/{song_id}/hqdefault.jpg",
                            "source": "youtube",
                        })
            return songs
        except subprocess.TimeoutExpired:
            log("  ⚠️ YouTube 搜索超时", style="yellow")
        except Exception as e:
            log(f"  ⚠️ YouTube 搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, song_id):
        if not self.available:
            return None
        try:
            url = f"https://www.youtube.com/watch?v={song_id}"
            result = subprocess.run(
                ["yt-dlp", "--no-download", "-g", "-f", "bestaudio", url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None

    def download(self, song_id, output_path, title="", artist=""):
        """直接用 yt-dlp 下载并转码为 mp3"""
        if not self.available:
            return False
        try:
            url = f"https://www.youtube.com/watch?v={song_id}"
            result = subprocess.run(
                ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320K",
                 "-o", output_path, url],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                # 写 ID3 标签
                actual_path = output_path.replace(".%(ext)s", ".mp3")
                if os.path.exists(actual_path):
                    embed_id3_tags(actual_path, title=title, artist=artist)
                return True
        except Exception as e:
            log(f"  ❌ YouTube 下载失败: {e}", style="red")
        return False


# ─── Bilibili ────────────────────────────────────────────────────────────────

class BilibiliClient:
    """Bilibili 音频下载"""

    SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"

    def search(self, keyword, limit=10):
        params = {
            "search_type": "video", "keyword": keyword,
            "page": 1, "pagesize": limit, "order": "totalrank",
        }
        try:
            resp = SESSION.get(self.SEARCH_URL, params=params, timeout=10)
            data = resp.json()
            if data.get("data", {}).get("result"):
                songs = []
                for s in data["data"]["result"][:limit]:
                    duration_str = s.get("duration", "0:00")
                    parts = duration_str.split(":")
                    try:
                        dur_sec = int(parts[0]) * 60 + int(parts[1]) if len(parts) == 2 else 0
                    except:
                        dur_sec = 0
                    songs.append({
                        "id": s.get("bvid", ""),
                        "name": s.get("title", "").replace("<em class=\"keyword\">", "").replace("</em>", ""),
                        "artists": s.get("author", ""),
                        "album": "",
                        "duration": dur_sec * 1000,
                        "cover": f"https:{s.get('pic', '')}" if s.get('pic') else "",
                        "source": "bilibili",
                    })
                return songs
        except Exception as e:
            log(f"  ⚠️ Bilibili 搜索失败: {e}", style="yellow")
        return []

    def get_song_url(self, bvid):
        """通过 yt-dlp 获取 B站 音频流"""
        if not HAS_YTDLP:
            return None
        try:
            url = f"https://www.bilibili.com/video/{bvid}"
            result = subprocess.run(
                ["yt-dlp", "--no-download", "-g", "-f", "bestaudio", url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")[0]
        except Exception:
            pass
        return None

    def download(self, bvid, output_path, title="", artist=""):
        """直接用 yt-dlp 下载 B站 视频音频"""
        if not HAS_YTDLP:
            return False
        try:
            url = f"https://www.bilibili.com/video/{bvid}"
            result = subprocess.run(
                ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320K",
                 "-o", output_path, url],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                actual_path = output_path.replace(".%(ext)s", ".mp3")
                if os.path.exists(actual_path):
                    embed_id3_tags(actual_path, title=title, artist=artist)
                return True
        except Exception as e:
            log(f"  ❌ Bilibili 下载失败: {e}", style="red")
        return False


# ─── SoundCloud ──────────────────────────────────────────────────────────────

class SoundCloudClient:
    """SoundCloud 下载 (via yt-dlp)"""

    def __init__(self):
        self.available = HAS_YTDLP

    def search(self, keyword, limit=10):
        if not self.available:
            return []
        try:
            result = subprocess.run(
                ["yt-dlp", "--no-download", "--print", "%(id)s|%(title)s|%(duration)s|%(uploader)s",
                 f"scsearch{limit}:{keyword}"],
                capture_output=True, text=True, timeout=30
            )
            songs = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 3)
                    if len(parts) >= 4:
                        song_id, title, duration, uploader = parts[0], parts[1], parts[2], parts[3]
                        try:
                            dur_sec = int(duration) * 1000 if duration.isdigit() else 0
                        except:
                            dur_sec = 0
                        songs.append({
                            "id": song_id,
                            "name": title,
                            "artists": uploader,
                            "album": "",
                            "duration": dur_sec,
                            "cover": "",
                            "source": "soundcloud",
                        })
            return songs
        except Exception as e:
            log(f"  ⚠️ SoundCloud 搜索失败: {e}", style="yellow")
        return []

    def download(self, song_id, output_path, title="", artist=""):
        if not self.available:
            return False
        try:
            url = f"https://soundcloud.com/{song_id}"
            result = subprocess.run(
                ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320K",
                 "-o", output_path, url],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                actual_path = output_path.replace(".%(ext)s", ".mp3")
                if os.path.exists(actual_path):
                    embed_id3_tags(actual_path, title=title, artist=artist)
                return True
        except Exception as e:
            log(f"  ❌ SoundCloud 下载失败: {e}", style="red")
        return False


# ─── 主下载器 ────────────────────────────────────────────────────────────────

class MusicDownloader:
    SOURCES = {
        "netease": ("网易云音乐", NeteaseMusicClient),
        "qq": ("QQ音乐", QQMusicClient),
        "kugou": ("酷狗音乐", KugouMusicClient),
        "kuwo": ("酷我音乐", KuwoMusicClient),
        "migu": ("咪咕音乐", MiguMusicClient),
        "youtube": ("YouTube", YouTubeClient),
        "bilibili": ("Bilibili", BilibiliClient),
        "soundcloud": ("SoundCloud", SoundCloudClient),
    }

    def __init__(self, output_dir=None):
        self.output_dir = output_dir or DEFAULT_OUTPUT
        os.makedirs(self.output_dir, exist_ok=True)
        self.clients = {}
        for key, (_, cls) in self.SOURCES.items():
            self.clients[key] = cls()

    def search(self, keyword, sources=None, limit=10):
        """多平台搜索"""
        if sources is None:
            sources = list(self.SOURCES.keys())

        all_songs = []
        for src in sources:
            if src in self.clients:
                name = self.SOURCES[src][0]
                client = self.clients[src]
                # 跳过不可用的
                if hasattr(client, 'available') and not client.available:
                    log(f"  ⏭️ {name}: 不可用 (需要 yt-dlp)", style="dim")
                    continue
                log(f"  🔍 搜索 {name}...", style="dim")
                songs = client.search(keyword, limit)
                all_songs.extend(songs)
                status = "✅" if songs else "❌"
                log(f"  {status} {name}: 找到 {len(songs)} 首", style="green" if songs else "dim")
        return all_songs

    def download_song(self, song, output_dir=None):
        """下载单首歌曲"""
        src = song["source"]
        song_id = song["id"]
        name = song["name"]
        artists = song["artists"]
        cover = song.get("cover", "")

        client = self.clients.get(src)
        if not client:
            log(f"  ❌ 未知来源: {src}", style="red")
            return False

        out = output_dir or self.output_dir
        safe_name = sanitize_filename(f"{artists} - {name}")
        filepath = os.path.join(out, f"{safe_name}.mp3")

        if os.path.exists(filepath):
            log(f"  ⏭️ 已存在: {safe_name}", style="yellow")
            return True

        # YouTube/Bilibili/SoundCloud 用自带的 download 方法
        if src in ("youtube", "bilibili", "soundcloud"):
            log(f"  ⬇️ 下载: {safe_name}", style="cyan")
            ytdlp_path = os.path.join(out, f"{safe_name}.%(ext)s")
            if client.download(song_id, ytdlp_path, title=name, artist=artists):
                log(f"  ✅ 完成: {safe_name}", style="green")
                return True
            return False

        # 国内平台用 URL 下载
        url = client.get_song_url(song_id)
        if not url:
            log(f"  ❌ 无法获取播放链接: {name} - {artists}", style="red")
            return False

        log(f"  ⬇️ 下载: {safe_name}", style="cyan")
        if download_file(url, filepath):
            size = os.path.getsize(filepath)
            if size < 10000:
                log(f"  ❌ 文件太小 ({size} bytes)，可能下载失败", style="red")
                os.remove(filepath)
                return False
            # 写 ID3 标签
            embed_id3_tags(filepath, title=name, artist=artists, album=song.get("album", ""), cover_url=cover if cover.startswith("http") else None)
            log(f"  ✅ 完成: {safe_name} ({size // 1024}KB)", style="green")
            return True
        return False

    def search_and_download(self, keyword, sources=None, limit=5, auto_download=False):
        """搜索并下载"""
        log(f"\n🎵 全网搜索: {keyword}\n", style="bold cyan")

        songs = self.search(keyword, sources, limit)
        if not songs:
            log("❌ 没有找到歌曲", style="red")
            return

        # 显示结果 - 纯文本格式 (兼容 TG)
        print("\n🎵 搜索结果\n")
        for i, s in enumerate(songs, 1):
            src_name = self.SOURCES.get(s["source"], (s["source"],))[0]
            dur = format_duration(s["duration"])
            album = s["album"] if s["album"] else ""
            print(f"{i}. {s['name']} | {s['artists']} | {album} | {dur} | {src_name}")
        
        # 保存结果到临时文件，方便外部调用者读取
        result_file = "/tmp/musicdl_results.json"
        with open(result_file, "w", encoding="utf-8") as rf:
            json.dump(songs, rf, ensure_ascii=False, indent=2)

        if auto_download:
            log(f"\n⬇️ 自动下载前 {min(3, len(songs))} 首...\n", style="bold")
            for s in songs[:3]:
                self.download_song(s)
            return

        # 交互式选择
        try:
            choice = input("\n输入序号下载 (多个用逗号分隔, 0=全部, q=退出): ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if choice.lower() == "q":
            return
        if choice == "0":
            for s in songs:
                self.download_song(s)
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(",")]
                for idx in indices:
                    if 0 <= idx < len(songs):
                        self.download_song(songs[idx])
            except ValueError:
                log("❌ 无效输入", style="red")


def main():
    parser = argparse.ArgumentParser(
        description="🎵 全网音乐下载工具 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s search "周杰伦 晴天"              # 全网搜索并交互下载
  %(prog)s search "周杰伦 晴天" -a           # 自动下载前3首
  %(prog)s search "周杰伦 晴天" -s netease qq  # 只搜指定平台
  %(prog)s search "周杰伦 晴天" -s youtube bilibili  # 只搜海外/视频平台
  %(prog)s download <url>                    # 直接下载URL

支持平台: netease(网易云), qq(QQ音乐), kugou(酷狗), kuwo(酷我), migu(咪咕), youtube, bilibili, soundcloud
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # search
    sp_search = subparsers.add_parser("search", help="搜索并下载")
    sp_search.add_argument("keyword", help="搜索关键词")
    sp_search.add_argument("-s", "--sources", nargs="+",
                           choices=["netease", "qq", "kugou", "kuwo", "migu", "youtube", "bilibili", "soundcloud"],
                           help="指定搜索源 (默认: 全部)")
    sp_search.add_argument("-l", "--limit", type=int, default=10, help="每源搜索结果数 (默认: 10)")
    sp_search.add_argument("-a", "--auto", action="store_true", help="自动下载前3首")
    sp_search.add_argument("-o", "--output", help="输出目录")

    # download
    sp_dl = subparsers.add_parser("download", help="直接下载URL")
    sp_dl.add_argument("url", help="音乐文件URL")
    sp_dl.add_argument("-o", "--output", help="输出目录")
    sp_dl.add_argument("-n", "--name", help="文件名")

    # info
    sp_info = subparsers.add_parser("info", help="查看工具状态")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "info":
        print("🎵 全网音乐下载工具 v2.0\n")
        print(f"  yt-dlp:     {'✅ 可用' if HAS_YTDLP else '❌ 未安装'}")
        print(f"  mutagen:    {'✅ 可用' if HAS_MUTAGEN else '❌ 未安装'}")
        print(f"  rich:       {'✅ 可用' if HAS_RICH else '❌ 未安装'}")
        print(f"  输出目录:   {DEFAULT_OUTPUT}")
        print()
        print("  国内平台: 网易云✅ | QQ音乐✅ | 酷狗✅ | 酷我⚠️ | 咪咕⚠️")
        print("  海外平台: YouTube | SoundCloud | Bilibili (需 yt-dlp)")
        return

    dl = MusicDownloader(output_dir=args.output if hasattr(args, "output") and args.output else None)

    if args.command == "search":
        dl.search_and_download(
            args.keyword,
            sources=args.sources,
            limit=args.limit,
            auto_download=args.auto,
        )
    elif args.command == "download":
        out = args.output or DEFAULT_OUTPUT
        os.makedirs(out, exist_ok=True)
        filepath = os.path.join(out, args.name or "download.mp3")
        log(f"⬇️ 下载到: {filepath}", style="cyan")
        if download_file(args.url, filepath):
            log(f"✅ 完成!", style="green")


if __name__ == "__main__":
    main()
