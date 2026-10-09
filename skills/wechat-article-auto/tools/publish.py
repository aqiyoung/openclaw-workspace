#!/usr/bin/env python3
"""
微信公众号自动化发布工具
一键完成：去AI润色 → 封面生成 → 上传草稿
用法: python publish.py <markdown文件路径> [--author 作者名] [--digest 摘要]
"""
import sys, os, json, re, math, argparse
from pathlib import Path
from datetime import datetime

# 添加工具目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from wechat_api import WeChatAPI, html_to_wechat_html

# ==================== 去AI化引擎 ====================

def deai_text(text: str) -> str:
    """
    去AI化处理：把八股文风改成真人说话
    """
    # 1. 替换模板化连接词
    replacements = {
        r'首先[，,]': '',
        r'其次[，,]': '',
        r'再次[，,]': '',
        r'最后[，,]': '',
        r'综上所述[，,]？': '',
        r'总而言之[，,]？': '',
        r'总的来说[，,]？': '',
        r'总之[，,]？': '',
        r'值得注意的是[，,]？': '',
        r'需要指出的是[，,]？': '',
        r'不可否认[，,]？': '',
        r'显而易见[，,]？': '',
        r'不难看出[，,]？': '',
    }
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)

    # 2. 打破完美三段式：把长段落拆成不等长的
    paragraphs = text.split('\n\n')
    new_paras = []
    for p in paragraphs:
        # 超过200字的段落拆分
        if len(p) > 200 and not p.startswith('```') and not p.startswith('#') and not p.startswith('|'):
            # 按句号拆分
            sentences = re.split(r'(?<=[。！？])', p)
            sentences = [s.strip() for s in sentences if s.strip()]
            if len(sentences) >= 3:
                mid = len(sentences) // 2
                new_paras.append(''.join(sentences[:mid]))
                new_paras.append(''.join(sentences[mid:]))
            else:
                new_paras.append(p)
        else:
            new_paras.append(p)
    text = '\n\n'.join(new_paras)

        # 3. 替换过于书面的表达
    casual_replacements = {
        '因此': '所以',
        '然而': '但是',
        '此外': '另外',
        '与此同时': '同时',
        '基于上述': '照上面说的',
        '综上': '总的来说',
        '值得注意的是': '要注意的是',
        '需要强调的是': '得说一下',
        '在一定程度上': '某种程度上',
        '具有重要意义': '很重要',
        '发挥重要作用': '很关键',
        '进行深入分析': '好好看看',
        '采取有效措施': '想办法',
        '实现预期目标': '搞定',
        '提供有力保障': '兜底',
    }
    for formal, casual in casual_replacements.items():
        text = text.replace(formal, casual)

    return text


def deai_markdown(filepath: str) -> str:
    """
    对Markdown文件做去AI化处理
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 分离front matter（如果有）
    front_matter = ''
    body = content
    
    # 处理正文（跳过代码块和表格）
    lines = body.split('\n')
    result = []
    in_code_block = False
    in_table = False
    paragraph_buffer = []
    
    def flush_paragraph():
        if paragraph_buffer:
            para = '\n'.join(paragraph_buffer)
            # 只对普通段落做去AI处理，跳过代码/表格/标题
            if not para.strip().startswith(('```', '|', '#', '>', '-', '*', '1.', '2.', '3.')):
                para = deai_text(para)
            result.append(para)
            paragraph_buffer.clear()
    
    for line in lines:
        if line.strip().startswith('```'):
            flush_paragraph()
            in_code_block = not in_code_block
            result.append(line)
        elif in_code_block:
            result.append(line)
        elif line.strip().startswith('|'):
            flush_paragraph()
            in_table = True
            result.append(line)
        elif in_table:
            if line.strip() == '' or not line.strip().startswith('|'):
                in_table = False
                result.append(line)
            else:
                result.append(line)
        elif line.strip() == '':
            flush_paragraph()
            result.append('')
        else:
            paragraph_buffer.append(line)
    
    flush_paragraph()
    return '\n'.join(result)


# ==================== 封面生成引擎 ====================

def generate_cover(output_path: str, title: str = None) -> str:
    """
    生成900x500科技感封面图
    """
    from PIL import Image, ImageDraw, ImageFont
    
    FONT_BOLD = r'C:\Windows\Fonts\simhei.ttf'
    FONT_REGULAR = r'C:\Windows\Fonts\msyh.ttc'
    
    width, height = 900, 500
    img = Image.new('RGB', (width, height), color='#0d1b2a')
    draw = ImageDraw.Draw(img)
    
    # 渐变背景
    for y in range(height):
        ratio = y / height
        r = int(13 + ratio * 15)
        g = int(27 + ratio * 30)
        b = int(42 + ratio * 45)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # 网格
    for x in range(0, width, 60):
        draw.line([(x, 0), (x, height)], fill=(40, 50, 70), width=1)
    for y in range(0, height, 60):
        draw.line([(0, y), (width, y)], fill=(40, 50, 70), width=1)
    
    # 服务器图标（右侧）
    def draw_server(x, y, w, h):
        draw.rectangle([x, y, x+w, y+h], fill='#1b263b', outline='#415a77', width=2)
        draw.ellipse([x+8, y+8, x+16, y+16], fill='#00ff88')
        draw.ellipse([x+22, y+8, x+30, y+16], fill='#4cc9f0')
        for i in range(3):
            yy = y + 25 + i * 18
            draw.rectangle([x+8, yy, x+w-8, yy+12], fill='#0d1b2a', outline='#415a77')
    
    draw_server(620, 60, 140, 90)
    draw_server(620, 170, 140, 90)
    draw_server(620, 280, 140, 90)
    
    # 连接线
    draw.line([(690, 150), (690, 170)], fill='#4cc9f0', width=2)
    draw.line([(690, 260), (690, 280)], fill='#4cc9f0', width=2)
    
    # 数据流箭头
    def draw_arrow(x1, y1, x2, y2, color='#4cc9f0'):
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
        angle = math.atan2(y2-y1, x2-x1)
        arrow_len = 10
        arrow_angle = 0.5
        ax1 = x2 - arrow_len * math.cos(angle - arrow_angle)
        ay1 = y2 - arrow_len * math.sin(angle - arrow_angle)
        ax2 = x2 - arrow_len * math.cos(angle + arrow_angle)
        ay2 = y2 - arrow_len * math.sin(angle + arrow_angle)
        draw.polygon([(x2, y2), (int(ax1), int(ay1)), (int(ax2), int(ay2))], fill=color)
    
    draw_arrow(100, 120, 580, 120)
    draw_arrow(100, 200, 580, 200)
    draw_arrow(100, 280, 580, 280)
    
    # 齿轮
    def draw_gear(cx, cy, r, teeth=10, color='#ff6d00'):
        points = []
        for i in range(teeth * 2):
            angle = i * math.pi / teeth
            radius = r if i % 2 == 0 else r * 0.75
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append((x, y))
        draw.polygon(points, fill=color, outline='#ff9e00')
        draw.ellipse([cx-r//3, cy-r//3, cx+r//3, cy+r//3], fill='#0d1b2a')
    
    draw_gear(100, 400, 45, teeth=12)
    draw_gear(180, 420, 30, teeth=8)
    draw_gear(60, 430, 25, teeth=6)
    
    # 代码符号
    try:
        font_code = ImageFont.truetype(FONT_BOLD, 18)
    except:
        font_code = ImageFont.load_default()
    
    for i, code in enumerate(['{ }', '< />', 'SQL', 'API', 'sudo']):
        draw.text((250 + i * 100, 430), code, fill='#00ff88', font=font_code)
    
    # 标题
    try:
        font_title = ImageFont.truetype(FONT_BOLD, 42)
        font_sub = ImageFont.truetype(FONT_REGULAR, 22)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
    
    # 标题背景
    draw.rectangle([40, 160, 560, 260], fill=(13, 27, 42), outline='#4cc9f0', width=2)
    
    # 标题文字（自动截断）
    display_title = title if title else "技术文章"
    if len(display_title) > 15:
        display_title = display_title[:15] + '...'
    draw.text((60, 170), display_title, fill='#ffffff', font=font_title)
    draw.text((60, 225), "技术分享 · 实战经验", fill='#4cc9f0', font=font_sub)
    
    # 边框和角落装饰
    draw.rectangle([15, 15, width-15, height-15], outline='#4cc9f0', width=2)
    corner = 40
    draw.line([(25, 25), (25+corner, 25)], fill='#f72585', width=3)
    draw.line([(25, 25), (25, 25+corner)], fill='#f72585', width=3)
    draw.line([(width-25, 25), (width-25-corner, 25)], fill='#f72585', width=3)
    draw.line([(width-25, 25), (width-25, 25+corner)], fill='#f72585', width=3)
    draw.line([(25, height-25), (25+corner, height-25)], fill='#f72585', width=3)
    draw.line([(25, height-25), (25, height-25-corner)], fill='#f72585', width=3)
    draw.line([(width-25, height-25), (width-25-corner, height-25)], fill='#f72585', width=3)
    draw.line([(width-25, height-25), (width-25, height-25-corner)], fill='#f72585', width=3)
    
    img.save(output_path, 'PNG')
    return output_path


# ==================== 主流程 ====================

def extract_title(content: str) -> str:
    """从Markdown提取标题"""
    for line in content.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return '未命名文章'


def extract_digest(content: str) -> str:
    """从Markdown提取摘要（第一个>引用）"""
    for line in content.split('\n'):
        if line.startswith('> '):
            return line[2:].strip()
    return ''


def main():
    parser = argparse.ArgumentParser(description='微信公众号自动化发布工具')
    parser.add_argument('article', help='Markdown文章文件路径')
    parser.add_argument('--author', default='三页札记', help='作者名')
    parser.add_argument('--digest', default='', help='文章摘要（不填则从文章>引用中提取）')
    parser.add_argument('--no-deai', action='store_true', help='跳过去AI化处理')
    parser.add_argument('--no-cover', action='store_true', help='跳过封面生成，使用默认封面')
    parser.add_argument('--cover-only', action='store_true', help='只生成封面，不上传草稿')
    
    args = parser.parse_args()
    
    article_path = Path(args.article).resolve()
    if not article_path.exists():
        print(f'ERROR: 文件不存在: {article_path}')
        sys.exit(1)
    
        print(f'[文章] {article_path.name}')
    
    # 读取原文
    with open(article_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    title = extract_title(original_content)
    digest = args.digest or extract_digest(original_content)
    
    print(f'[标题] {title}')
    if digest:
        print(f'[摘要] {digest[:50]}...')
    
    # Step 1: 去AI化
    if args.no_deai:
        print('[跳过] 去AI化')
        processed_content = original_content
    else:
        print('[处理] 去AI化中...')
        processed_content = deai_markdown(str(article_path))
        deai_path = article_path.parent / f'{article_path.stem}_deai{article_path.suffix}'
        with open(deai_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
            print(f'[完成] 去AI化: {deai_path.name}')
    
        # Step 2: 生成封面
    if args.no_cover and not args.cover_only:
        print('[跳过] 封面生成')
        cover_path = None
    else:
        print('[生成] 封面图...')
        cover_path = str(article_path.parent / f'{article_path.stem}_cover.png')
        generate_cover(cover_path, title)
        print(f'[完成] 封面: {Path(cover_path).name}')
    
    if args.cover_only:
        print(f'\n[完成] 封面生成: {cover_path}')
        return
    
    # Step 3: 上传到微信草稿箱
    print('[上传] 微信草稿箱...')
    api = WeChatAPI()
    
    html_content = html_to_wechat_html(processed_content)
    
    thumb_media_id = None
    if cover_path and Path(cover_path).exists():
        thumb_media_id = api.upload_image(cover_path)
        print(f'[完成] 封面上传: {thumb_media_id[:20]}...')
    else:
        thumb_media_id = api.config.get('default_thumb_media_id')
        if thumb_media_id:
            print(f'[使用] 默认封面')
    
    media_id = api.create_draft(
        title=title,
        content=html_content,
        author=args.author,
        thumb_media_id=thumb_media_id,
        digest=digest
    )
    
    print(f'\n[成功] 发布完成！')
    print(f'[标题] {title}')
    print(f'[草稿ID] {media_id}')
    print(f'[作者] {args.author}')
    if digest:
        print(f'[摘要] {digest[:50]}...')
    print(f'\n前往草稿箱: https://mp.weixin.qq.com/')


if __name__ == '__main__':
    main()
