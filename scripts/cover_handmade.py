#!/usr/bin/env python3
"""
手搓封面 v2 — 微信公众号 900x506 (2.35:1)
深蓝科技风 + 终端窗口 + 装饰元素
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, sys

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noto_sc.otf')
W, H = 900, 506

def load_font(size):
    if os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()

def center_text(draw, y, text, font, color, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=color, font=font)

def generate(output_path):
    img = Image.new('RGB', (W, H), '#0a0a2e')
    draw = ImageDraw.Draw(img)

    # === 背景渐变：深蓝到深青 ===
    for y in range(H):
        r = int(10 + (15 - 10) * y / H)
        g = int(10 + (30 - 10) * y / H)
        b = int(46 + (60 - 46) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # === 网格线（淡） ===
    for x in range(0, W, 40):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 12), width=1)
    for y in range(0, H, 40):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)

    # === 发光圆（右上） ===
    for r in range(200, 0, -2):
        alpha = int(30 * (1 - r/200))
        draw.ellipse([W - r - 100, -r - 30, W + 100, r + 30],
                     fill=(0, 180, 255))

    # === 发光圆（左下，小） ===
    for r in range(120, 0, -2):
        alpha = int(20 * (1 - r/120))
        draw.ellipse([-r - 20, H - r - 40, r + 20, H + 40],
                     fill=(120, 0, 255))

    # === 左侧装饰竖线 ===
    draw.rectangle([40, 80, 44, H - 80], fill=(0, 200, 255))

    # === 终端窗口 ===
    term_x, term_y = 50, H - 130
    term_w, term_h = 300, 100
    # 终端背景
    draw.rectangle([term_x, term_y, term_x + term_w, term_y + term_h],
                   fill=(0, 0, 0, 180), outline=(0, 200, 255), width=1)
    # 终端内容
    font_term = load_font(14)
    lines = [
        ('$ top', '#666666'),
        ('PID  USER   CPU%  COMMAND', '#00ccff'),
        ('2847  root   95.2  java', '#ff6b35'),
        ('1024  www    12.1  nginx', '#00ff88'),
        ('512   mysql   8.3  mysqld', '#00ff88'),
    ]
    for i, (line, color) in enumerate(lines):
        draw.text((term_x + 12, term_y + 10 + i * 18), line, fill=color, font=font_term)

    # === 右侧终端（小） ===
    term2_x = W - 220
    term2_y = 60
    draw.rectangle([term2_x, term2_y, term2_x + 170, term2_y + 80],
                   fill=(0, 0, 0, 120), outline=(0, 200, 255), width=1)
    font_term2 = load_font(11)
    lines2 = [
        ('$ htop', '#666666'),
        ('┌─────────────────────┐', '#00cc88'),
        ('│ CPU [|||||||95%]     │', '#ff6b35'),
        ('│ Mem [|||||67%]      │', '#00ccff'),
        ('└─────────────────────┘', '#00cc88'),
    ]
    for i, (line, color) in enumerate(lines2):
        draw.text((term2_x + 8, term2_y + 8 + i * 15), line, fill=color, font=font_term2)

    # === 标签 ===
    font_tag = load_font(14)
    tag = '🛠 运维实战'
    bbox = draw.textbbox((0, 0), tag, font=font_tag)
    tw = bbox[2] - bbox[0]
    # 标签背景
    tag_x = (W - tw) // 2 - 12
    draw.rectangle([tag_x, 60, tag_x + tw + 24, 88],
                   fill=(0, 150, 200), outline=(0, 200, 255), width=1)
    draw.text((tag_x + 12, 63), tag, fill=(255, 255, 255), font=font_tag)

    # === 主标题 ===
    font_title = load_font(48)
    title = '电脑越用越慢？'
    center_text(draw, 100, title, font_title, (255, 255, 255), W)

    # === 副标题（带强调色） ===
    font_sub = load_font(28)
    sub1 = '一条命令定位'
    sub2 = '元凶'
    bbox1 = draw.textbbox((0, 0), sub1, font=font_sub)
    w1 = bbox1[2] - bbox1[0]
    bbox2 = draw.textbbox((0, 0), sub2, font=font_sub)
    w2 = bbox2[2] - bbox2[0]
    
    # "一条命令定位" 偏左，"元凶" 偏右，中间留空
    total_w = w1 + 20 + w2
    start_x = (W - total_w) // 2
    draw.text((start_x, 170), sub1, fill=(200, 220, 255), font=font_sub)
    draw.text((start_x + w1 + 20, 170), sub2, fill=(0, 255, 136), font=font_sub)

    # === 分隔线 ===
    sep_y = 220
    draw.line([(W // 2 - 80, sep_y), (W // 2 + 80, sep_y)], fill=(0, 200, 255), width=2)

    # === 底部说明 ===
    font_small = load_font(16)
    desc = 'top / htop 命令详解'
    center_text(draw, 240, desc, font_small, (120, 140, 170), W)

    # === 右下角品牌 ===
    font_brand = load_font(14)
    brand = '三页札记'
    bbox = draw.textbbox((0, 0), brand, font=font_brand)
    bw = bbox[2] - bbox[0]
    draw.text((W - bw - 20, H - 25), brand, fill=(80, 100, 130), font=font_brand)

    # === 保存 ===
    img.save(output_path, 'PNG')
    size = os.path.getsize(output_path)
    print(f'✅ 封面图生成: {output_path}')
    print(f'   尺寸: {W}x{H}')
    print(f'   大小: {size} bytes ({size//1024}KB)')
    return output_path

if __name__ == '__main__':
    output = sys.argv[1] if len(sys.argv) > 1 else '/tmp/cover_handmade.png'
    generate(output)
