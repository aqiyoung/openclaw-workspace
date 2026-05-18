#!/usr/bin/env python3
import sys, os, json, time
from playwright.sync_api import sync_playwright

COOKIE_FILE = os.path.join(os.path.dirname(__file__), 'douyin-cookies.json')
CREATOR_URL = 'https://creator.douyin.com'

def login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        page.goto(CREATOR_URL, wait_until='networkidle', timeout=30000)
        time.sleep(5)
        
        # 截取登录页面
        qr_path = os.path.join(os.path.dirname(__file__), 'douyin-qr.png')
        page.screenshot(path=qr_path)
        print(f'QR_CODE_PATH:{qr_path}')
        print(f'URL:{page.url()}')
        print('请用微信扫码登录，等待中...')
        
        # 等待登录成功
        try:
            page.wait_for_url('**/creator-micro/**', timeout=120000)
            print('LOGIN_SUCCESS')
        except:
            # 检测其他登录标志
            try:
                page.wait_for_url('**/creator/**', timeout=5000)
                print('LOGIN_SUCCESS')
            except:
                print('LOGIN_TIMEOUT')
                browser.close()
                return
        
        # 保存 cookies
        cookies = context.cookies()
        with open(COOKIE_FILE, 'w') as f:
            json.dump(cookies, f, indent=2)
        print('COOKIES_SAVED')
        browser.close()

def publish(title, content, images):
    if not os.path.exists(COOKIE_FILE):
        print('ERROR:未登录，请先运行 login')
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        with open(COOKIE_FILE) as f:
            cookies = json.load(f)
        context.add_cookies(cookies)
        page = context.new_page()
        
        page.goto(f'{CREATOR_URL}/creator-micro/home', wait_until='networkidle', timeout=30000)
        time.sleep(3)
        
        # 检查登录状态
        if 'login' in page.url() or page.locator('text=扫码').first.is_visible():
            print('ERROR:Cookie过期，请重新 login')
            browser.close()
            return
        
        print(f'URL:{page.url()}')
        
        # 截取当前页面
        debug_path = os.path.join(os.path.dirname(__file__), 'douyin-debug.png')
        page.screenshot(path=debug_path)
        print(f'DEBUG_PATH:{debug_path}')
        print('PUBLISH_STUB:脚本已执行，需根据实际页面调整选择器')
        
        browser.close()

if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else ''
    if action == 'login':
        login()
    elif action == 'publish':
        title = sys.argv[2] if len(sys.argv) > 2 else ''
        content = sys.argv[3] if len(sys.argv) > 3 else ''
        images = sys.argv[4:]
        publish(title, content, images)
    else:
        print('用法:')
        print('  登录: python3 douyin-publish.py login')
        print('  发布: python3 douyin-publish.py publish "标题" "描述" img1.png')
