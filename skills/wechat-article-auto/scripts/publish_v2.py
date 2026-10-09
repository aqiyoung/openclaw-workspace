#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号自动化发布工具 - 美化版
功能：文章润色 → HTML美化 → 封面图生成 → 上传草稿箱
"""

import os
import sys
import json
import re
import time
import random
import hashlib
import requests
from pathlib import Path
from datetime import datetime

# 设置UTF-8输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入自定义模块
sys.path.insert(0, str(Path(__file__).parent))
from cover_generator import CoverGenerator
from wechat_html_converter import convert_markdown_to_wechat

class WeChatAutoPublisher:
    """微信公众号自动化发布工具"""
    
    # AI痕迹词汇检测列表
    AI_TRACES = [
        '首先', '其次', '最后', '综上所述', '总而言之', '总之',
        '第一', '第二', '第三', '一方面', '另一方面',
        '值得注意的是', '不可否认', '显而易见', '毋庸置疑',
        '在当今社会', '随着科技的发展', '日益重要'
    ]
    
    # 口语化替换词典（纯替换，不加标签）
    ORAL_REPLACEMENTS = {
        '因此': '所以',
        '然而': '但是',
        '具有重要意义': '很重要',
        '具有重大价值': '很有用',
        '值得注意的是': '有意思的是',
        '不可否认': '说实话',
        '显而易见': '很明显',
        '综上所述': '总结一下',
        '总而言之': '总的来说'
    }
    
    def __init__(self, config_path=None):
        """初始化配置"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        self.config = self.load_config(config_path)
        self.access_token = None
        self.token_expires_at = 0
        self.template_path = Path(__file__).parent.parent / "templates" / "article_template.html"
        
    def load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] 配置文件不存在: {config_path}")
            print("请复制 config.example.json 为 config.json 并填写配置")
            sys.exit(1)
    
    def get_access_token(self):
        """获取微信access_token"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        app_id = self.config['wechat']['app_id']
        app_secret = self.config['wechat']['app_secret']
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}"
        
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 300
                print("[OK] 获取access_token成功")
                return self.access_token
            else:
                print(f"[ERROR] 获取access_token失败: {data}")
                return None
        except Exception as e:
            print(f"[ERROR] 获取access_token异常: {e}")
            return None
    
    def polish_article(self, content):
        """AI去味润色（干净替换，不加口语化标签）"""
        print("[START] 开始AI去味润色...")
        
        lines = content.split('\n')
        polished_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                polished_lines.append(line)
                continue
            
            if in_code_block:
                polished_lines.append(line)
                continue
            
            polished_line = line
            # 替换AI痕迹词汇（仅替换，不添加任何额外内容）
            for ai_word, replacement in self.ORAL_REPLACEMENTS.items():
                polished_line = polished_line.replace(ai_word, replacement)
            
            polished_lines.append(polished_line)
        
        result = '\n'.join(polished_lines)
        
        # 检测是否还有AI痕迹
        remaining_traces = [t for t in self.AI_TRACES if t in result]
        if remaining_traces:
            print(f"[WARN] 仍有AI痕迹: {', '.join(remaining_traces[:3])}")
        else:
            print("[OK] AI痕迹已清除")
        
        print("[OK] 润色完成")
        return result
    
    def markdown_to_html(self, markdown_content):
        """Markdown转HTML（使用专业转换器）"""
        return convert_markdown_to_wechat(markdown_content)
    
    def render_html_template(self, title, content_html, author=None, no_meta=False):
        """使用模板渲染HTML"""
        print("[START] 渲染HTML模板...")
        
        if no_meta:
            # 简洁模式：应用模板样式，但去掉头部/底部装饰
            print("[OK] 简洁模式，应用模板样式（无装饰）")
            # 读取模板提取样式
            if not self.template_path.exists():
                print("[WARN] 模板文件不存在，使用简单HTML")
                return content_html
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 提取style标签
            import re
            style_match = re.search(r'<style>(.*?)</style>', template, re.DOTALL)
            if style_match:
                styles = style_match.group(0)
                # 组合：样式 + 内容
                html = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>{title}</title>\n    {styles}\n</head>\n<body>\n    <div class="article-container">\n        <div class="article-content">\n            {content_html}\n        </div>\n    </div>\n</body>\n</html>'
                ).format(title=title, styles=styles, content_html=content_html)
                return html
            else:
                return content_html
        
        # 读取模板
        if not self.template_path.exists():
            print("[WARN] 模板文件不存在，使用简单HTML")
            return content_html
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 替换模板变量
        html = template
        html = html.replace('{{title}}', title)
        html = html.replace('{{content}}', content_html)
        html = html.replace('{{author}}', author or self.config['wechat'].get('default_author', 'AI助手'))
        
        print("[OK] HTML渲染完成")
        return html
    
    def generate_cover(self, title, output_path, style="tech", author=None):
        """生成封面图"""
        print("[START] 开始生成封面图...")
        
        generator = CoverGenerator()
        result = generator.generate(
            title=title,
            output_path=output_path,
            style=style,
            author=author
        )
        
        return result
    
    def upload_image_to_wechat(self, image_path):
        """上传图片到微信素材库"""
        print(f"[START] 上传图片到微信...")
        
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
        
        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                resp = requests.post(url, files=files, timeout=30)
            
            data = resp.json()
            
            if 'media_id' in data:
                print("[OK] 图片上传成功")
                return data['media_id']
            else:
                print(f"[ERROR] 图片上传失败: {data.get('errmsg', '未知错误')}")
                return None
        except Exception as e:
            print(f"[ERROR] 图片上传异常: {e}")
            return None
    
    def create_draft(self, title, content, author=None, digest=None, cover_media_id=None):
        """创建微信公众号草稿"""
        print("[START] 创建草稿...")
        
        access_token = self.get_access_token()
        if not access_token:
            return None
        
        if author is None:
            author = self.config['wechat'].get('default_author', 'AI助手')
        
        # 微信作者名限制：约30字节（不是字符！）
        while len(author.encode('utf-8')) > 30:
            author = author[:-1]
        if len(author) < len(self.config['wechat'].get('default_author', 'AI助手')):
            print(f"[WARN] 作者名过长，已截断为: {author}")
        
        if digest is None:
            # fallback：从HTML正文提取摘要
            clean_content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
            clean_content = re.sub(r'<[^>]+>', '', clean_content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            if not clean_content:
                clean_content = 'AI大模型最新动态'
            max_bytes = 117
            digest = ""
            for char in clean_content:
                test = digest + char
                if len(test.encode('utf-8')) > max_bytes:
                    break
                digest = test
            if len(clean_content.encode('utf-8')) > max_bytes:
                while len(digest.encode('utf-8')) > max_bytes - 3:
                    digest = digest[:-1]
                digest += '...'
        
        # 确保标题不超过微信限制（64字节，不是字符！）
        while len(title.encode('utf-8')) > 64:
            title = title[:-1]
        if len(title) < len(title):  # 如果被截断了
            print(f"[WARN] 标题过长，已截断为: {title}")
        
        articles = [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": self.config['wechat'].get('content_source_url', ''),
            "need_open_comment": self.config['wechat'].get('need_open_comment', 0),
            "only_fans_can_comment": self.config['wechat'].get('only_fans_can_comment', 0)
        }]
        
        if cover_media_id:
            articles[0]["thumb_media_id"] = cover_media_id
        
        data = {"articles": articles}
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        # 关键修复：禁用ASCII转义，保留中文字符，指定UTF-8编码
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        post_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        
        try:
            resp = requests.post(url, data=post_data, headers=headers, timeout=30)
            result = resp.json()
            
            if 'media_id' in result:
                print("[OK] 草稿创建成功")
                return result['media_id']
            else:
                print(f"[ERROR] 草稿创建失败: {result.get('errmsg', '未知错误')}")
                return None
        except Exception as e:
            print(f"[ERROR] 草稿创建异常: {e}")
            return None
    
    def process_article(self, article_path, style="tech", author=None, digest=None, 
                        no_deai=False, no_cover=False, cover_only=False, no_meta=False):
        """处理文章的完整流程"""
        # 读取文章
        article_path = Path(article_path)
        if not article_path.exists():
            print(f"[ERROR] 文章不存在: {article_path}")
            return {"success": False, "error": "文章不存在"}
        
        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 从文件名或内容提取标题
        title = article_path.stem
        # 尝试从内容第一行获取标题
        first_line = content.split('\n')[0].strip()
        if first_line.startswith('#'):
            title = first_line.lstrip('#').strip()
        
        print(f"\n{'='*50}")
        print(f"[PROCESS] 开始处理文章: {title}")
        print(f"{'='*50}\n")
        
        output_dir = article_path.parent
        base_name = article_path.stem
        
        # 1. AI去味润色
        if not no_deai:
            polished_content = self.polish_article(content)
            # 保存润色后的内容
            polished_path = output_dir / f"{base_name}_deai.md"
            with open(polished_path, 'w', encoding='utf-8') as f:
                f.write(polished_content)
            print(f"[SAVE] 润色版已保存: {polished_path}")
        else:
            polished_content = content
            print("[SKIP] 跳过去AI化")
        
        if cover_only:
            # 只生成封面
            cover_path = output_dir / f"{base_name}_cover.png"
            self.generate_cover(title, str(cover_path), style, author)
            return {"success": True, "cover_path": str(cover_path)}
        
        # 如果没提供摘要，从原始markdown提取（避免HTML里的style/css代码混入）
        if digest is None:
            md_text = re.sub(r'^#.*$', '', polished_content, flags=re.MULTILINE)
            md_text = re.sub(r'```.*?```', '', md_text, flags=re.DOTALL)
            md_text = re.sub(r'[#*`\[\]()!<>\-|_]', '', md_text)
            md_text = re.sub(r'\s+', ' ', md_text).strip()
            max_bytes = 117
            digest = ""
            for char in md_text:
                test = digest + char
                if len(test.encode('utf-8')) > max_bytes:
                    break
                digest = test
            if len(md_text.encode('utf-8')) > max_bytes:
                while len(digest.encode('utf-8')) > max_bytes - 3:
                    digest = digest[:-1]
                digest += '...'
        
        # 2. 转换为HTML
        content_html = self.markdown_to_html(polished_content)
        html_content = self.render_html_template(title, content_html, author, no_meta)
        
        # 保存HTML文件
        html_path = output_dir / f"{base_name}_html.txt"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"[SAVE] HTML已保存: {html_path}")
        
        # 3. 生成封面图
        cover_path = None
        cover_media_id = None
        
        if not no_cover:
            cover_path = str(output_dir / f"{base_name}_cover.png")
            # 简洁模式下封面不显示作者
            cover_author = None if no_meta else author
            self.generate_cover(title, cover_path, style, cover_author)
            
            # 4. 上传封面图
            if cover_path and os.path.exists(cover_path):
                cover_media_id = self.upload_image_to_wechat(cover_path)
        
        # 5. 创建草稿
        draft_media_id = self.create_draft(
            title=title,
            content=html_content,
            author=author,
            digest=digest,
            cover_media_id=cover_media_id
        )
        
        print(f"\n{'='*50}")
        if draft_media_id:
            print("[SUCCESS] 文章处理完成！")
            print(f"[DRAFT] 草稿ID: {draft_media_id}")
            print("[LINK] 管理地址: https://mp.weixin.qq.com/")
            print(f"{'='*50}")
            return {
                "success": True,
                "draft_media_id": draft_media_id,
                "cover_path": cover_path,
                "polished_path": str(polished_path) if not no_deai else None,
                "html_path": str(html_path)
            }
        else:
            print("[FAIL] 文章处理失败")
            print(f"{'='*50}")
            return {
                "success": False,
                "error": "草稿创建失败",
                "polished_path": str(polished_path) if not no_deai else None,
                "html_path": str(html_path)
            }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='微信公众号自动化发布工具')
    parser.add_argument('article', help='文章文件路径（Markdown格式）')
    parser.add_argument('--style', default='tech', choices=['tech', 'story', 'opinion'],
                        help='润色风格（默认：tech，仅 --deai 时生效）')
    parser.add_argument('--author', help='作者名称')
    parser.add_argument('--digest', help='文章摘要，不传自动从正文提取')
    parser.add_argument('--deai', action='store_true', 
                        help='开启AI去味润色（默认关闭，推荐手动保证自然度）')
    parser.add_argument('--with-meta', action='store_true', 
                        help='开启模板头部/底部装饰（默认简洁模式）')
    parser.add_argument('--no-cover', action='store_true', help='跳过封面图生成')
    parser.add_argument('--cover-only', action='store_true', help='只生成封面图')
    parser.add_argument('--cover-style', default='tech', 
                        choices=['tech', 'ocean', 'sunset', 'forest', 'dark', 'purple'],
                        help='封面风格（默认：tech）')
    parser.add_argument('--config', help='配置文件路径')
    
    args = parser.parse_args()
    
    publisher = WeChatAutoPublisher(args.config)
    
    # 默认行为反转：no_deai=True（默认干净），no_meta=True（默认简洁）
    result = publisher.process_article(
        article_path=args.article,
        style=args.style,
        author=args.author,
        digest=args.digest,
        no_deai=not args.deai,          # 默认不润色
        no_cover=args.no_cover,
        cover_only=args.cover_only,
        no_meta=not args.with_meta       # 默认无装饰
    )
    
    if result['success']:
        print("\n[DONE] 处理成功！")
        if result.get('draft_media_id'):
            print(f"草稿ID: {result['draft_media_id']}")
        if result.get('cover_path'):
            print(f"封面图: {result['cover_path']}")
    else:
        print(f"\n[FAIL] 处理失败: {result.get('error', '未知错误')}")
        sys.exit(1)


if __name__ == '__main__':
    main()