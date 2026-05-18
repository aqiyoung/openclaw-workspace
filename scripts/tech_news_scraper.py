#!/usr/bin/env python3
"""科技/AI 新闻聚合抓取器 - Playwright 版"""
from playwright.sync_api import sync_playwright
import json, re, socket
from datetime import datetime

PROXY = "http://127.0.0.1:7890"

def _proxy_available():
    """检查代理是否可用"""
    try:
        with socket.create_connection(("127.0.0.1", 7890), timeout=2):
            return True
    except Exception:
        return False

class TechNewsScraper:
    def __init__(self):
        self.articles = []
        self.p = None
        self.browser = None
        self.use_proxy = _proxy_available()
    
    def start(self):
        self.p = sync_playwright().start()
        launch_args = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if self.use_proxy:
            launch_args["proxy"] = {"server": PROXY}
            print("🔌 使用代理模式")
        else:
            print("⚡ 代理不可用，使用直连模式")
        self.browser = self.p.chromium.launch(**launch_args)
    
    def stop(self):
        try:
            if self.browser: self.browser.close()
        except Exception:
            pass
        try:
            if self.p: self.p.stop()
        except Exception:
            pass
    
    def _page(self):
        return self.browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    def scrape_36kr(self):
        """36氪 科技 + AI"""
        for cat, url in [
            ("科技", "https://36kr.com/information/technology/"),
            ("AI", "https://36kr.com/information/AI/"),
        ]:
            try:
                page = self._page()
                page.goto(url, timeout=20000, wait_until="domcontentloaded")
                page.wait_for_timeout(3000)
                
                links = page.query_selector_all("a")
                seen = set()
                for link in links:
                    text = (link.text_content() or "").strip()
                    href = link.get_attribute("href") or ""
                    if len(text) > 12 and "/p/" in href and text not in seen:
                        seen.add(text)
                        if href.startswith("/"):
                            href = "https://36kr.com" + href
                        self.articles.append({"source": f"36氪-{cat}", "title": text, "url": href})
                page.close()
            except Exception as e:
                print(f"36氪-{cat} 失败: {e}")
    
    def scrape_hackernews(self):
        """Hacker News AI/Tech 热门"""
        try:
            page = self._page()
            page.goto("https://hn.algolia.com/?dateRange=pastWeek&page=0&prefix=true&query=AI+OR+LLM+OR+GPT&sort=byPopularity&type=story",
                      timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            items = page.query_selector_all(".Story_title a")
            for item in items[:15]:
                title = (item.text_content() or "").strip()
                href = item.get_attribute("href") or ""
                if title and len(title) > 5:
                    if href.startswith("/"):
                        href = "https://news.ycombinator.com" + href
                    self.articles.append({"source": "HackerNews", "title": title, "url": href})
            page.close()
        except Exception as e:
            print(f"HackerNews 失败: {e}")
    
    def scrape_v2ex(self):
        """V2EX 技术节点"""
        try:
            page = self._page()
            page.goto("https://www.v2ex.com/go/programming", timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            
            items = page.query_selector_all(".item_title a")
            for item in items[:10]:
                title = (item.text_content() or "").strip()
                href = item.get_attribute("href") or ""
                if title:
                    if href.startswith("/"):
                        href = "https://www.v2ex.com" + href
                    self.articles.append({"source": "V2EX", "title": title, "url": href})
            page.close()
        except Exception as e:
            print(f"V2EX 失败: {e}")
    
    def scrape_techcrunch(self):
        """TechCrunch AI"""
        try:
            page = self._page()
            page.goto("https://techcrunch.com/category/artificial-intelligence/", timeout=25000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            links = page.query_selector_all("a.post-card-title__link, h2 a, h3 a, .article-hero a")
            for link in links[:10]:
                title = (link.text_content() or "").strip()
                href = link.get_attribute("href") or ""
                if title and len(title) > 10:
                    self.articles.append({"source": "TechCrunch-AI", "title": title, "url": href})
            page.close()
        except Exception as e:
            print(f"TechCrunch 失败: {e}")
    
    def scrape_ithome(self):
        """IT之家 AI 频道"""
        try:
            page = self._page()
            page.goto("https://www.ithome.com/ai/", timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)
            
            links = page.query_selector_all("a")
            seen = set()
            for link in links:
                text = (link.text_content() or "").strip()
                href = link.get_attribute("href") or ""
                if 10 < len(text) < 80 and ("ithome.com" in href or href.startswith("/")) and text not in seen:
                    seen.add(text)
                    if href.startswith("/"):
                        href = "https://www.ithome.com" + href
                    if re.match(r'https?://www\.ithome\.com/\d', href):
                        self.articles.append({"source": "IT之家", "title": text, "url": href})
            page.close()
        except Exception as e:
            print(f"IT之家 失败: {e}")
    
    def scrape_sspai(self):
        """少数派"""
        try:
            page = self._page()
            page.goto("https://sspai.com/tag/ai", timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            
            links = page.query_selector_all("a")
            seen = set()
            for link in links:
                text = (link.text_content() or "").strip()
                href = link.get_attribute("href") or ""
                if 10 < len(text) < 80 and "/post/" in href and text not in seen:
                    seen.add(text)
                    if href.startswith("/"):
                        href = "https://sspai.com" + href
                    self.articles.append({"source": "少数派", "title": text, "url": href})
            page.close()
        except Exception as e:
            print(f"少数派 失败: {e}")
    
    def run_all(self):
        self.start()
        scrapers = [
            ("36氪", self.scrape_36kr),
            ("HackerNews", self.scrape_hackernews),
            ("V2EX", self.scrape_v2ex),
            ("TechCrunch", self.scrape_techcrunch),
            ("IT之家", self.scrape_ithome),
            ("少数派", self.scrape_sspai),
        ]
        for name, fn in scrapers:
            print(f"🔄 抓取 {name}...")
            fn()
            count = len([a for a in self.articles if a["source"].startswith(name) or name in a["source"]])
            print(f"   ✅ {name} 完成")
        self.stop()
        return self.articles

if __name__ == "__main__":
    import sys
    scraper = TechNewsScraper()
    try:
        articles = scraper.run_all()
    except Exception as e:
        print(f"❌ 抓取出错: {e}")
        scraper.stop()
        sys.exit(1)
    finally:
        scraper.stop()
    
    # 按来源分组输出
    print("\n" + "="*60)
    print(f"📰 科技/AI 新闻聚合 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    by_source = {}
    for a in articles:
        by_source.setdefault(a["source"], []).append(a)
    
    for source, items in by_source.items():
        print(f"\n🔷 {source} ({len(items)}条)")
        print("-"*40)
        for i, item in enumerate(items[:8], 1):
            print(f"  {i}. {item['title']}")
            print(f"     {item['url']}")
    
    print(f"\n📊 共 {len(articles)} 条科技/AI新闻")
    
    # 保存到文件
    with open("/tmp/tech_news.json", "w", encoding="utf-8") as f:
        json.dump({"time": datetime.now().isoformat(), "articles": articles}, f, ensure_ascii=False, indent=2)
    print("💾 已保存到 /tmp/tech_news.json")
