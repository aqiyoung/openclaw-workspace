#!/usr/bin/env python3
"""
x-monitor.py — X/Twitter 监控脚本
监控指定账号时间线的所有新推文（包括转发、引用）
输出格式：NEW_TWEETS:JSON 或 NO_NEW_TWEETS
"""

import json
import time
import re
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

NITTER_URL = "http://127.0.0.1:8080"
MONITORED_USERS = ["OpenRouter", "_LuoFuli", "elonmusk", "NVIDIAAI", "openclaw", "steipete"]
STATE_FILE = Path.home() / ".openclaw" / "x-monitor-state.json"
LOG_FILE = Path.home() / ".openclaw" / "x-monitor.log"
MAX_STATE = 500

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(line + "\n")
    except:
        pass

def load_state():
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            if len(state.get("tweets", {})) > MAX_STATE:
                sorted_ids = sorted(state["tweets"].keys(), reverse=True)
                state["tweets"] = {k: state["tweets"][k] for k in sorted_ids[:300]}
            return state
        except:
            pass
    return {"tweets": {}}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def clean_html(text):
    """清理 HTML 标签"""
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    return text.strip()

def check_user(username):
    """检查单个账号时间线的所有推文（包括转发）"""
    for attempt in range(3):
        try:
            url = f"{NITTER_URL}/{username}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                html = r.read().decode("utf-8", errors="ignore")
            
            tweets = []
            # 提取每个推文块
            blocks = re.findall(
                r'class="timeline-item[^"]*"[^>]*data-username="([^"]+)".*?class="tweet-body"[^>]*>(.*?)</div>\s*<div class="tweet-stats"',
                html, re.DOTALL
            )
            
            seen_ids = set()
            for tweet_user, body in blocks:
                # 提取推文链接
                link_match = re.search(r'href="(/[^"]+/status/(\d+))[#"]', body)
                if not link_match:
                    continue
                link = link_match.group(1).split('#')[0]
                tweet_id = link_match.group(2)
                
                if tweet_id in seen_ids:
                    continue
                seen_ids.add(tweet_id)
                
                # 提取正文
                # 提取正文（匹配 tweet-content media-body）
                content_match = re.search(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', body, re.DOTALL)
                if not content_match:
                    content_match = re.search(r'class="tweet-content[^"]*"[^>]*>(.*?)</div>', body, re.DOTALL)
                content = clean_html(content_match.group(1)) if content_match else ""
                
                # 提取转发信息
                retweet_match = re.search(r'class="retweet-header"[^>]*>(.*?)</div>', body, re.DOTALL)
                retweet_info = ""
                if retweet_match:
                    retweet_text = clean_html(retweet_match.group(1))
                    retweet_info = retweet_text.replace("retweeted", "转发")
                
                # 提取引用/回复信息
                quote_match = re.search(r'class="quote quote-body"[^>]*>(.*?)</div>', body, re.DOTALL)
                quote_content = ""
                if quote_match:
                    quote_content = clean_html(quote_match.group(1))
                
                # 提取时间（从 class="tweet-date" 下的 a 标签 title 属性）
                time_match = re.search(r'class="tweet-date"[^>]*>.*?<a[^>]*title="([^"]+)"', body, re.DOTALL)
                time_str = time_match.group(1) if time_match else ""
                
                # 提取统计
                stats = re.findall(r'class="tweet-stat"[^>]*>.*?(\d[\d,]*)\s*</div>', body, re.DOTALL)
                
                tweet = {
                    "id": tweet_id,
                    "url": f"https://x.com{link}",
                    "username": tweet_user,
                    "content": content[:500],  # 限制长度
                    "retweet_info": retweet_info[:100] if retweet_info else "",
                    "quote_content": quote_content[:300] if quote_content else "",
                    "time": time_str,
                    "source_account": username,  # 来源账号（被监控的账号）
                }
                tweets.append(tweet)
            
            return tweets[:1]  # 每个账号只取最新1条
        
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = (attempt + 1) * 15
                log(f"  Rate limited @{username}, waiting {wait}s...")
                time.sleep(wait)
                continue
            log(f"  HTTP Error @{username}: {e}")
            return []
        except Exception as e:
            log(f"  Error @{username}: {e}")
            return []
    return []

def main():
    state = load_state()
    new_tweets = []
    
    log(f"Checking {len(MONITORED_USERS)} users...")
    
    for username in MONITORED_USERS:
        tweets = check_user(username)
        for tweet in tweets:
            tweet_id = tweet["id"]
            if tweet_id not in state["tweets"]:
                state["tweets"][tweet_id] = {
                    "username": tweet["username"],
                    "source_account": tweet["source_account"],
                    "url": tweet["url"],
                    "content": tweet["content"],
                    "time": datetime.now().isoformat()
                }
                new_tweets.append(tweet)
                preview = tweet["content"][:50] if tweet["content"] else "[无文字]"
                log(f"  🆕 @{tweet['username']}: {preview}")
        time.sleep(2)
    
    save_state(state)
    
    if new_tweets:
        print(f"NEW_TWEETS:{json.dumps(new_tweets, ensure_ascii=False)}", flush=True)
    else:
        print("NO_NEW_TWEETS", flush=True)

if __name__ == "__main__":
    main()
