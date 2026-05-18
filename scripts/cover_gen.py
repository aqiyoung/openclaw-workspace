#!/usr/bin/env python3
"""
封面图生成脚本 - 微信公众号 2400x1350
用法: python3 cover_gen.py 风格编号 主标题 [副标题] [输出路径]

风格:
  1 = 深蓝渐变（科技感/教程）
  2 = 深绿渐变（稳重/运维）
  3 = 黄黑警告（踩坑/故障）
  4 = 白底简约（干净/观点）
  5 = 暗紫渐变（经验分享/故事）← NEW
  6 = 橙红渐变（热点/观点）← NEW
  7 = 纯黑极简（高级/深度）← NEW
  8 = 深灰橙（运维/排障）← NEW
  9 = 深灰橙·升级版（无竖线/光晕装饰/大字体/留白）← NEW
"""

import sys
from PIL import Image, ImageDraw, ImageFont
import os

FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'noto_sc.otf')
OUTPUT_DIR = '/tmp'

STYLES = {
    1: {
        'name': '深蓝渐变',
        'bg_start': (10, 20, 40),
        'bg_end': (20, 60, 120),
        'accent': (0, 180, 255),
        'text': (255, 255, 255),
        'sub': (180, 200, 230),
    },
    2: {
        'name': '深绿渐变',
        'bg_start': (10, 30, 20),
        'bg_end': (30, 80, 50),
        'accent': (80, 220, 120),
        'text': (255, 255, 255),
        'sub': (180, 230, 200),
    },
    3: {
        'name': '黄黑警告',
        'bg_start': (30, 25, 10),
        'bg_end': (60, 50, 20),
        'accent': (255, 200, 0),
        'text': (255, 255, 255),
        'sub': (230, 210, 160),
    },
    4: {
        'name': '白底简约',
        'bg_start': (245, 247, 250),
        'bg_end': (235, 238, 242),
        'accent': (0, 100, 200),
        'text': (30, 40, 50),
        'sub': (100, 110, 120),
    },
    5: {
        'name': '暗紫渐变',
        'bg_start': (20, 10, 35),
        'bg_end': (50, 25, 80),
        'accent': (160, 80, 220),
        'text': (255, 255, 255),
        'sub': (200, 180, 230),
    },
    6: {
        'name': '橙红渐变',
        'bg_start': (40, 15, 10),
        'bg_end': (100, 30, 20),
        'accent': (255, 100, 50),
        'text': (255, 255, 255),
        'sub': (240, 200, 180),
    },
    7: {
        'name': '纯黑极简',
        'bg_start': (5, 5, 5),
        'bg_end': (15, 15, 15),
        'accent': (255, 255, 255),
        'text': (255, 255, 255),
        'sub': (120, 120, 120),
    },
    8: {
        'name': '深灰橙',
        'bg_start': (25, 28, 32),
        'bg_end': (35, 38, 45),
        'accent': (255, 140, 50),
        'text': (240, 240, 240),
        'sub': (160, 160, 160),
    },
    9: {
        'name': '深灰橙·升级版',
        'bg_start': (15, 15, 25),
        'bg_end': (35, 35, 50),
        'accent': (255, 140, 0),
        'text': (255, 255, 255),
        'sub': (200, 200, 200),
    },
}

W, H = 2400, 1350


def load_font(size):
    if os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()


def draw_gradient(draw, color_start, color_end, w, h):
    for y in range(h):
        r = int(color_start[0] + (color_end[0] - color_start[0]) * y / h)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * y / h)
        b = int(color_start[2] + (color_end[2] - color_start[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def center_text(draw, y, text, font, color, width):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (width - tw) // 2
    draw.text((x, y), text, fill=color, font=font)


def wrap_text(text, font, max_width, draw):
    lines = []
    chars = list(text)
    current = ''
    for ch in chars:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def draw_decoration(draw, style_id, s):
    if style_id == 1:
        # 科技网格 + 光晕
        for x in range(0, W, 80):
            draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 15), width=1)
        for y in range(0, H, 80):
            draw.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=1)
        for r in range(400, 0, -2):
            draw.ellipse([W - r - 200, -r - 50, W + 200, r + 50],
                         fill=(s['accent'][0], s['accent'][1], s['accent'][2]))

    elif style_id == 2:
        # 底部横条 + 左侧竖条
        draw.rectangle([0, H - 8, W, H], fill=s['accent'])
        draw.rectangle([0, 0, 8, H], fill=s['accent'])

    elif style_id == 3:
        # 顶部红色条 + 底部红色条
        draw.rectangle([0, 0, W, 12], fill=(255, 60, 0))
        draw.rectangle([0, H - 8, W, H], fill=(255, 60, 0))

    elif style_id == 4:
        # 顶部细线 + 底部细线
        draw.rectangle([0, 0, W, 4], fill=s['accent'])
        draw.rectangle([0, H - 4, W, H], fill=(200, 200, 200))

    elif style_id == 5:
        # 暗紫：左侧竖条 + 右下角光晕
        draw.rectangle([60, 150, 68, H - 150], fill=s['accent'])
        for r in range(280, 0, -3):
            draw.ellipse([W - r - 120, H - r - 80, W + 120, H + 80],
                         fill=(s['accent'][0], s['accent'][1], s['accent'][2]))

    elif style_id == 6:
        # 橙红：对角线条纹 + 顶部条
        for i in range(-H, W, 60):
            draw.line([(i, 0), (i + H, H)], fill=(255, 255, 255, 8), width=1)
        draw.rectangle([0, 0, W, 6], fill=s['accent'])

    elif style_id == 7:
        # 纯黑：底部细线
        draw.rectangle([0, H - 2, W, H], fill=(40, 40, 40))

    elif style_id == 8:
        # 深灰橙：顶部橙条 + 底部橙条
        draw.rectangle([0, 0, W, 12], fill=s['accent'])
        draw.rectangle([0, H - 8, W, H], fill=s['accent'])

    elif style_id == 9:
        # 深灰橙·升级版：顶部橙条 + 底部橙条 + 光晕 + 装饰线 + 点阵
        draw.rectangle([0, 0, W, 12], fill=s['accent'])
        draw.rectangle([0, H - 8, W, H], fill=s['accent'])
        # 左上角光晕
        for r in range(600, 0, -2):
            draw.ellipse([-r + 200, -r + 100, r + 200, r + 100],
                         fill=(s['accent'][0], s['accent'][1], s['accent'][2]))
        # 右下角光晕（暗蓝）
        for r in range(500, 0, -2):
            draw.ellipse([W - r - 100, H - r - 50, W + r - 100, H + r - 50],
                         fill=(40, 80, 160))
        # 右侧装饰竖线
        for i in range(5):
            x = W - 300 - i * 60
            y_start = 200 + i * 40
            y_end = y_start + 150 - i * 20
            draw.line([(x, y_start), (x, y_end)],
                      fill=(s['accent'][0], s['accent'][1], s['accent'][2]), width=2)
        # 左侧点阵
        for i in range(8):
            x = 100 + (i % 3) * 40
            y = 300 + i * 50
            size = 3 + (i % 4)
            draw.ellipse([x - size, y - size, x + size, y + size], fill=s['accent'])


def generate(style_id, title, subtitle='', output_path=None):
    s = STYLES.get(style_id, STYLES[1])
    img = Image.new('RGB', (W, H))
    draw = ImageDraw.Draw(img)

    # 渐变背景
    draw_gradient(draw, s['bg_start'], s['bg_end'], W, H)

    # 装饰元素
    draw_decoration(draw, style_id, s)

    # 风格 5/7/8/9 有自己的竖线或装饰，跳过额外竖线
    if style_id not in (5, 7, 8, 9):
        draw.rectangle([80, 200, 88, H - 200], fill=s['accent'])

    # 主标题字号自适应（风格9用更大字号）
    if style_id == 9:
        title_font_size = 120 if len(title) <= 12 else 100 if len(title) <= 16 else 80
    else:
        title_font_size = 90 if len(title) <= 10 else 75 if len(title) <= 15 else 60
    font_title = load_font(title_font_size)

    # 标题自动换行
    title_lines = wrap_text(title, font_title, W - 200, draw)
    title_y = 300
    line_spacing = int(title_font_size * 1.4)
    for i, line in enumerate(title_lines[:3]):
        center_text(draw, title_y + i * line_spacing, line, font_title, s['text'], W)

    # 分隔线（风格9不需要）
    sep_y = title_y + len(title_lines[:3]) * line_spacing + 40
    if style_id != 9:
        draw.line([(W // 2 - 150, sep_y), (W // 2 + 150, sep_y)], fill=s['accent'], width=3)

    # 副标题
    if subtitle:
        font_sub_size = 52 if style_id == 9 else 42
        font_sub = load_font(font_sub_size)
        sub_lines = wrap_text(subtitle, font_sub, W - 200, draw)
        # 风格9：主标题下方留一行空白
        if style_id == 9:
            sub_y = sep_y + 80
        else:
            sub_y = sep_y + 40
        for i, line in enumerate(sub_lines[:2]):
            center_text(draw, sub_y + i * 60, line, font_sub, s['sub'], W)

    # 底部品牌（风格9不需要）
    if style_id != 9:
        font_brand = load_font(36)
        brand = '三页札记'
        bbox = draw.textbbox((0, 0), brand, font=font_brand)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, H - 100), brand, fill=s['sub'], font=font_brand)

    # 保存
    if not output_path:
        output_path = f'{OUTPUT_DIR}/cover_{style_id}.png'
    img.save(output_path, quality=100)
    print(f'✅ 封面图生成: {output_path}')
    print(f'   风格: {s["name"]}')
    print(f'   尺寸: {W}x{H}')
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    style_id = int(sys.argv[1])
    title = sys.argv[2]
    subtitle = sys.argv[3] if len(sys.argv) > 3 else ''
    output_path = sys.argv[4] if len(sys.argv) > 4 else None

    generate(style_id, title, subtitle, output_path)
