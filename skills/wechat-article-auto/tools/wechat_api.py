"""
微信公众号API工具
用于获取access_token、上传图片、创建草稿等操作
"""

import json
import os
import sys
import time
import re
import requests
from pathlib import Path


def decode_unicode(obj):
    """递归解码字典/列表中的Unicode转义序列（支持单反斜杠和双反斜杠）"""
    if isinstance(obj, dict):
        return {k: decode_unicode(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decode_unicode(item) for item in obj]
    elif isinstance(obj, str):
        def replace_unicode(match):
            return chr(int(match.group(1), 16))
        # 处理单反斜杠 \uXXXX（微信API返回的格式）
        result = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, obj)
        return result
    else:
        return obj


class WeChatAPI:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        self.config_path = config_path
        self.base_url = "https://api.weixin.qq.com/cgi-bin"

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_access_token(self):
        """获取access_token，如果过期则自动刷新"""
        now = int(time.time() * 1000)

        # 检查token是否有效
        if self.config.get('access_token') and self.config.get('token_expires_at', 0) > now:
            return self.config['access_token']

        # 刷新token
        url = f"{self.base_url}/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.config['app_id'],
            'secret': self.config['app_secret']
        }

        resp = requests.get(url, params=params)
        data = resp.json()

        if 'access_token' not in data:
            raise Exception(f"获取access_token失败: {data}")

        # 保存token，有效期7200秒，提前5分钟过期
        self.config['access_token'] = data['access_token']
        self.config['token_expires_at'] = now + (data.get('expires_in', 7200) - 300) * 1000
        self.save_config()

        return data['access_token']

    def upload_image(self, image_path):
        """上传图片获取media_id"""
        token = self.get_access_token()
        url = f"{self.base_url}/material/add_material?access_token={token}"

        with open(image_path, 'rb') as f:
            files = {'media': f}
            data = {'type': 'image'}
            resp = requests.post(url, files=files, data=data)
            result = resp.json()

        if 'media_id' not in result:
            raise Exception(f"上传图片失败: {result}")

        return result['media_id']

    def create_draft(self, title, content, author=None, thumb_media_id=None, digest=''):
        """
        创建草稿文章

        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            author: 作者名（可选）
            thumb_media_id: 封面图media_id（可选）
            digest: 文章摘要（可选）

        Returns:
            media_id: 草稿media_id
        """
        token = self.get_access_token()
        url = f"{self.base_url}/draft/add?access_token={token}"

        # 确保标题不超过微信限制（14字节 GBK编码）
        # 微信标题限制是14字节（GBK编码），中文字符占2字节
        title_bytes = len(title.encode('gbk', errors='replace'))
        if title_bytes >= 14:
            # 截断到14字节以内
            truncated = []
            current_bytes = 0
            for char in title:
                char_bytes = len(char.encode('gbk', errors='replace'))
                if current_bytes + char_bytes > 12:  # 留2字节余量
                    break
                truncated.append(char)
                current_bytes += char_bytes
            title = ''.join(truncated)
            print(f"[WARN] 标题过长，已截断为: {title}")

        # 确保摘要不超过微信限制（120字节 GBK编码）
        # 微信摘要限制是120字节（GBK编码），中文字符占2字节
        if digest:
            digest_bytes = len(digest.encode('gbk', errors='replace'))
            if digest_bytes >= 120:
                # 截断到120字节以内
                truncated = []
                current_bytes = 0
                for char in digest:
                    char_bytes = len(char.encode('gbk', errors='replace'))
                    if current_bytes + char_bytes > 118:  # 留2字节余量
                        break
                    truncated.append(char)
                    current_bytes += char_bytes
                digest = ''.join(truncated) + '...'
                print(f"[WARN] 摘要过长，已截断为: {digest}")

        # 构建文章对象
        article = {
            'title': title,
            'content': content,
            'content_source_url': '',
            'need_open_comment': 1,
            'only_fans_can_comment': 0
        }

        # 作者（可选）
        final_author = author or self.config.get('default_author', '')
        if final_author and len(final_author.encode('utf-8')) <= 8:  # 微信公众号作者名最长8个字节
            article['author'] = final_author

        # 封面图（可选，必须有效）
        final_thumb = thumb_media_id or self.config.get('default_thumb_media_id')
        if final_thumb:
            if isinstance(final_thumb, tuple):
                final_thumb = final_thumb[0]  # 兼容旧的返回格式
            if isinstance(final_thumb, str) and final_thumb.strip() != '':
                article['thumb_media_id'] = final_thumb

        # 摘要（可选）
        if digest:
            article['digest'] = digest

        payload = {
            'articles': [article]
        }

        # 使用ensure_ascii=False确保中文不被转义
        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        resp = requests.post(url, data=json_data, headers={
            'Content-Type': 'application/json; charset=utf-8'
        })
        result = resp.json()

        if 'media_id' not in result:
            raise Exception(f"创建草稿失败: {result}")

        return result['media_id']

    def get_draft_list(self, offset=0, count=20):
        """获取草稿列表"""
        token = self.get_access_token()
        url = f"{self.base_url}/draft/batchget?access_token={token}"

        payload = {
            'offset': offset,
            'count': count,
            'no_content': 0
        }

        resp = requests.post(url, json=payload, headers={
            'Content-Type': 'application/json'
        })

        # 修复编码问题：微信API返回的JSON可能编码错误
        try:
            # 首先尝试正常解析
            result = resp.json()
        except:
            # 如果失败，尝试修复编码
            raw_bytes = resp.content
            try:
                # 尝试用UTF-8解码
                text = raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                # 如果UTF-8失败，尝试用Latin-1解码，然后重新编码为UTF-8
                text = raw_bytes.decode('latin-1')
            result = json.loads(text)
        
        # 修复标题和摘要的编码问题
        if 'item' in result:
            for item in result['item']:
                if 'content' in item and 'news_item' in item['content']:
                    for news_item in item['content']['news_item']:
                        # 修复标题编码
                        if 'title' in news_item:
                            title = news_item['title']
                            if isinstance(title, str):
                                # 检查是否是错误编码的UTF-8
                                try:
                                    # 尝试将字符串编码为Latin-1，然后解码为UTF-8
                                    fixed_title = title.encode('latin-1').decode('utf-8')
                                    news_item['title'] = fixed_title
                                except (UnicodeEncodeError, UnicodeDecodeError):
                                    pass
                        
                        # 修复摘要编码
                        if 'digest' in news_item:
                            digest = news_item['digest']
                            if isinstance(digest, str):
                                try:
                                    fixed_digest = digest.encode('latin-1').decode('utf-8')
                                    news_item['digest'] = fixed_digest
                                except (UnicodeEncodeError, UnicodeDecodeError):
                                    pass
        
        return decode_unicode(result)

    def delete_draft(self, media_id):
        """删除草稿"""
        token = self.get_access_token()
        url = f"{self.base_url}/draft/delete?access_token={token}"

        payload = {
            'media_id': media_id
        }

        json_data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        resp = requests.post(url, data=json_data, headers={
            'Content-Type': 'application/json; charset=utf-8'
        })

        return resp.json()


def html_to_wechat_html(markdown_content):
    """
    将Markdown内容转换为微信公众号兼容的HTML
    使用微信公众号标准格式：section标签 + 换行
    """
    html = markdown_content

    # 标题转换 - 使用section包裹
    html = re.sub(r'^### (.+)$', r'<section><h3>\1</h3></section>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<section><h2>\1</h2></section>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<section><h1>\1</h1></section>', html, flags=re.MULTILINE)

    # 粗体和斜体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # 代码块
    html = re.sub(r'```(\w*)\n(.*?)```', r'<section><pre><code>\2</code></pre></section>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # 列表 - 先转li，再包裹ul
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

    # 收集连续的li并包裹ul
    lines = html.split('\n')
    result = []
    li_buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('<li>'):
            li_buffer.append(stripped)
        else:
            if li_buffer:
                result.append('<section><ul>' + ''.join(li_buffer) + '</ul></section>')
                li_buffer = []
            result.append(line)

    if li_buffer:
        result.append('<section><ul>' + ''.join(li_buffer) + '</ul></section>')

    html = '\n'.join(result)

    # 段落 - 跳过已有的HTML标签行
    paragraphs = html.split('\n\n')
    processed = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 如果已经是HTML标签开头，直接保留
        if p.startswith('<'):
            processed.append(p)
        else:
            processed.append(f'<section><p>{p}</p></section>')
    html = '\n'.join(processed)

    # 图片标注
    html = re.sub(r'\[图片：(.+?)\]', r'<section><p style="text-align:center;color:#999;font-size:12px;">【配图：\1】</p></section>', html)

    return html


if __name__ == '__main__':
    api = WeChatAPI()
    print(f"AppID: {api.config['app_id']}")
    print("API初始化成功")
