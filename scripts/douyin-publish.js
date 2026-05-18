const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const COOKIE_FILE = path.join(__dirname, 'douyin-cookies.json');
const CREATOR_URL = 'https://creator.douyin.com';

// 登录 - headless 模式，提取二维码发给用户
async function login() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();
  
  await page.goto(CREATOR_URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  // 提取二维码图片
  const qrSelectors = [
    'img[class*="qr"]',
    'img[class*="QR"]', 
    'img[class*="code"]',
    'img[class*="login"]',
    '.qrcode img',
    '#qrcode img',
    'img[alt*="二维码"]',
    'img[alt*="QR"]'
  ];
  
  let qrFound = false;
  for (const sel of qrSelectors) {
    const el = page.locator(sel).first();
    if (await el.isVisible().catch(() => false)) {
      const qrPath = path.join(__dirname, 'douyin-qr.png');
      await el.screenshot({ path: qrPath });
      console.log(`QR_CODE_PATH:${qrPath}`);
      qrFound = true;
      break;
    }
  }
  
  if (!qrFound) {
    // 截取整个登录区域
    const qrPath = path.join(__dirname, 'douyin-qr.png');
    await page.screenshot({ path: qrPath, fullPage: false });
    console.log(`QR_CODE_PATH:${qrPath}`);
  }
  
  console.log('等待扫码...');
  
  // 等待登录成功（URL 变化）
  try {
    await page.waitForURL('**/creator-micro/**', { timeout: 120000 });
    console.log('LOGIN_SUCCESS');
  } catch {
    // 检测其他登录成功的标志
    const isLoggedIn = await page.locator('text=发布作品, text=创作, text=数据中心').first()
      .isVisible().catch(() => false);
    if (isLoggedIn) {
      console.log('LOGIN_SUCCESS');
    } else {
      console.log('LOGIN_TIMEOUT');
      await browser.close();
      return;
    }
  }
  
  // 保存 cookies
  const cookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
  console.log('COOKIES_SAVED');
  
  await browser.close();
}

// 发布图文
async function publishImageText(title, content, images) {
  if (!fs.existsSync(COOKIE_FILE)) {
    console.log('ERROR:未登录，请先 login');
    return;
  }
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const cookies = JSON.parse(fs.readFileSync(COOKIE_FILE, 'utf8'));
  await context.addCookies(cookies);
  const page = await context.newPage();
  
  // 进入创作者后台
  await page.goto(`${CREATOR_URL}/creator-micro/home`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  // 检查是否需要重新登录
  const needLogin = await page.locator('text=登录, text=扫码').first()
    .isVisible().catch(() => false);
  if (needLogin) {
    console.log('ERROR:Cookie过期，请重新 login');
    await browser.close();
    return;
  }
  
  // 点击发布按钮
  const publishBtn = page.locator('text=发布作品, text=发布, text=创作').first();
  await publishBtn.click();
  await page.waitForTimeout(2000);
  
  // 选择图文模式
  const imageTab = page.locator('text=图文').first();
  if (await imageTab.isVisible().catch(() => false)) {
    await imageTab.click();
    await page.waitForTimeout(1000);
  }
  
  // 上传图片
  const fileInput = page.locator('input[type="file"]').first();
  for (const imgPath of images) {
    if (fs.existsSync(imgPath)) {
      await fileInput.setInputFiles(imgPath);
      await page.waitForTimeout(3000);
      console.log(`UPLOADED:${path.basename(imgPath)}`);
    }
  }
  
  // 填写标题
  const titleInput = page.locator('[placeholder*="标题"], [placeholder*="title"]').first();
  if (await titleInput.isVisible().catch(() => false)) {
    await titleInput.fill(title);
  }
  
  // 填写描述
  const descInput = page.locator('[placeholder*="描述"], [placeholder*="说点"], textarea').first();
  if (await descInput.isVisible().catch(() => false)) {
    await descInput.fill(content);
  }
  
  // 截图确认
  const confirmPath = path.join(__dirname, 'douyin-confirm.png');
  await page.screenshot({ path: confirmPath });
  console.log(`CONFIRM_PATH:${confirmPath}`);
  
  // 发布
  const submitBtn = page.locator('button:has-text("发布"), button:has-text("发表"), button:has-text("确认")').first();
  if (await submitBtn.isVisible().catch(() => false)) {
    await submitBtn.click();
    await page.waitForTimeout(3000);
    console.log('PUBLISH_SUCCESS');
  } else {
    console.log('PUBLISH_FAILED:找不到发布按钮');
  }
  
  // 更新 cookies
  const newCookies = await context.cookies();
  fs.writeFileSync(COOKIE_FILE, JSON.stringify(newCookies, null, 2));
  
  await browser.close();
}

// 命令行入口
const action = process.argv[2];

if (action === 'login') {
  login().catch(e => console.log('ERROR:' + e.message));
} else if (action === 'publish') {
  const title = process.argv[3] || '';
  const content = process.argv[4] || '';
  const images = process.argv.slice(5);
  publishImageText(title, content, images).catch(e => console.log('ERROR:' + e.message));
} else {
  console.log('用法:');
  console.log('  登录: node douyin-publish.js login');
  console.log('  发布: node douyin-publish.js publish "标题" "描述" img1.png img2.png');
}
