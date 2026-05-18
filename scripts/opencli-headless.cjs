#!/usr/bin/env node
/**
 * opencli-headless — 不依赖 Chrome Extension 的 headless 浏览器 CLI
 * 用 puppeteer-core + 系统 Chromium 实现 OpenCLI 核心功能
 * 
 * 用法:
 *   node opencli-headless.cjs open <url>
 *   node opencli-headless.cjs snapshot <url>
 *   node opencli-headless.cjs screenshot <url> [outPath]
 *   node opencli-headless.cjs extract <url>
 *   node opencli-headless.cjs links <url>
 */

const puppeteer = require(require('path').join(require('child_process').execSync('npm root -g').toString().trim(), 'puppeteer-core'));

const CDP_PORT = 9222;
const BROWSER_URL = `http://127.0.0.1:${CDP_PORT}`;

async function ensureBrowser() {
  try {
    const r = await fetch(`${BROWSER_URL}/json/version`, { signal: AbortSignal.timeout(2000) });
    if (r.ok) return { browserURL: BROWSER_URL };
  } catch {}
  
  console.error('Starting headless Chromium...');
  const { spawn } = require('node:child_process');
  const proc = spawn('chromium', [
    '--headless=new', '--no-sandbox', '--disable-gpu',
    '--disable-dev-shm-usage', '--disable-extensions',
    '--disable-background-networking', '--disable-default-apps',
    `--remote-debugging-port=${CDP_PORT}`,
    '--remote-debugging-address=127.0.0.1',
    '--user-data-dir=/tmp/opencli-headless-profile',
    'about:blank'
  ], { stdio: 'pipe' });
  
  for (let i = 0; i < 20; i++) {
    await new Promise(r => setTimeout(r, 1000));
    try {
      const r = await fetch(`${BROWSER_URL}/json/version`, { signal: AbortSignal.timeout(2000) });
      if (r.ok) return { browserURL: BROWSER_URL, _proc: proc };
    } catch {}
  }
  throw new Error('Failed to start Chromium');
}

async function cmdOpen(page, url) {
  const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  return { url: page.url(), title: await page.title(), status: resp?.status() };
}

async function cmdSnapshot(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const title = await page.title();
  const text = await page.evaluate(() => document.body?.innerText?.slice(0, 5000) || '');
  return { title, url: page.url(), text };
}

async function cmdScreenshot(page, url, outPath) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const path = outPath || `/tmp/screenshot-${Date.now()}.png`;
  await page.screenshot({ path, fullPage: false });
  return { path, title: await page.title() };
}

async function cmdExtract(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const result = await page.evaluate(() => {
    const article = document.querySelector('article') || document.querySelector('main') || document.body;
    if (!article) return { title: document.title, text: '' };
    const clone = article.cloneNode(true);
    for (const el of clone.querySelectorAll('script,style,nav,footer,header,aside,iframe,noscript,[role=banner],[role=navigation],[role=complementary]')) {
      el.remove();
    }
    return {
      title: document.title,
      text: clone.innerText?.trim().slice(0, 8000) || '',
      byline: document.querySelector('[rel=author]')?.textContent?.trim() || '',
      published: document.querySelector('time')?.getAttribute('datetime') || ''
    };
  });
  return result;
}

async function cmdLinks(page, url) {
  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
  const links = await page.evaluate(() =>
    Array.from(document.querySelectorAll('a[href]'))
      .filter(a => a.href.startsWith('http'))
      .map(a => ({ text: a.textContent.trim().slice(0, 100), href: a.href }))
      .filter(l => l.text.length > 0)
      .slice(0, 50)
  );
  return { title: await page.title(), url: page.url(), links };
}

// ─── CLI ───────────────────────────────────────────────────────────

const [,, cmd, url, ...rest] = process.argv;

if (!cmd || !url) {
  console.log(`opencli-headless v1.0.0

Usage:
  opencli-headless open <url>              Open page, return title+status
  opencli-headless snapshot <url>          Get text snapshot
  opencli-headless screenshot <url> [path] Screenshot
  opencli-headless extract <url>           Extract article text
  opencli-headless links <url>             Extract all links
`);
  process.exit(0);
}

const commands = { open: cmdOpen, snapshot: cmdSnapshot, screenshot: cmdScreenshot, extract: cmdExtract, links: cmdLinks };

if (!commands[cmd]) {
  console.error(`Unknown command: ${cmd}`);
  process.exit(1);
}

(async () => {
  try {
    const opts = await ensureBrowser();
    const browser = await puppeteer.connect(opts);
    const page = await browser.newPage();
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36');
    const result = await commands[cmd](page, url, ...rest);
    console.log(JSON.stringify(result, null, 2));
    await page.close();
    await browser.disconnect();
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
})();
