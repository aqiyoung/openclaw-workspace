#!/usr/bin/env python3
"""快速推送草稿 - 支持自定义封面"""
import json, requests, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from wechat_html_converter import convert_markdown_to_wechat

# Config
APP_ID = 'wx97bc84bb54232e27'
APP_SECRET = '31dd5e8ce9bf116d1b5ca3b81c2d82ea'

def get_token():
    resp = requests.get(f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}', timeout=15)
    return resp.json()['access_token']

def upload_image(token, path):
    with open(path, 'rb') as f:
        resp = requests.post(f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image', files={'media': ('cover.jpg', f, 'image/jpeg')}, timeout=30)
    return resp.json()['media_id']

def create_draft(token, title, author, digest, html_content, cover_media_id):
    payload = {
        'articles': [{
            'title': title,
            'author': author,
            'digest': digest,
            'content': html_content,
            'thumb_media_id': cover_media_id,
            'show_cover_pic': 1,
        }]
    }
    json_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    resp = requests.post(
        f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}',
        data=json_bytes,
        headers={'Content-Type': 'application/json; charset=utf-8'},
        timeout=15
    )
    return resp.json()

if __name__ == '__main__':
    article_path = sys.argv[1] if len(sys.argv) > 1 else '/home/liyang/.openclaw/workspace/文章-OpenClaw经验分享.md'
    cover_path = sys.argv[2] if len(sys.argv) > 2 else None
    author = sys.argv[3] if len(sys.argv) > 3 else '三页'
    
    token = get_token()
    print('Got token')
    
    # Upload cover
    if cover_path:
        cover_media_id = upload_image(token, cover_path)
        print(f'Cover uploaded: {cover_media_id[:30]}...')
    else:
        cover_media_id = None
    
    # Convert markdown to HTML
    with open(article_path, 'r', encoding='utf-8') as f:
        md = f.read()
    html = convert_markdown_to_wechat(md)
    print(f'HTML length: {len(html)}')
    
    # Get title from first line
    title = 'OpenClaw体验分享'
    digest = '一个月真实使用体验'
    
    # Create draft
    result = create_draft(token, title, author, digest, html, cover_media_id)
    print(f'Result: {json.dumps(result, ensure_ascii=False)}')
    if 'media_id' in result:
        print(f'✅ Draft: {result["media_id"]}')
