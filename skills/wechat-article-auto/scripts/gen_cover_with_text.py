#!/usr/bin/env python3
"""生成公众号封面图 - AI底图 + 标题文字"""
from PIL import Image, ImageDraw, ImageFont
import os

# 加载AI生成的底图
ai_img = Image.open('/home/liyang/.openclaw/workspace/文章-OpenClaw经验分享_cover_ai4.jpg')
print(f'AI image size: {ai_img.size}')

# 裁切为 900x500
w, h = ai_img.size
target_ratio = 900 / 500
current_ratio = w / h

if current_ratio > target_ratio:
    new_w = int(h * target_ratio)
    left = (w - new_w) // 2
    ai_img = ai_img.crop((left, 0, left + new_w, h))
else:
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    ai_img = ai_img.crop((0, top, w, top + new_h))

ai_img = ai_img.resize((900, 500), Image.LANCZOS)
print(f'Cropped to: {ai_img.size}')

# 绘制文字
draw = ImageDraw.Draw(ai_img)

# 字体
misans_regular = '/home/liyang/.local/share/fonts/MiSans/MiSans-Regular.ttf'
misans_bold = '/home/liyang/.local/share/fonts/MiSans/MiSans-Bold.ttf'

# 半透明底部遮罩
overlay = Image.new('RGBA', (900, 500), (0, 0, 0, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle([(0, 300), (900, 500)], fill=(0, 0, 0, 120))
# 将底图转为RGBA
ai_img_rgba = ai_img.convert('RGBA')
# 合成
composite = Image.alpha_composite(ai_img_rgba, overlay)
ai_img = composite.convert('RGB')
draw = ImageDraw.Draw(ai_img)

# 主标题
title = '我用OpenClaw一个月'
title2 = '才发现AI原来可以这样用'

try:
    font_title = ImageFont.truetype(misans_bold, 42)
    font_title2 = ImageFont.truetype(misans_bold, 36)
    font_sub = ImageFont.truetype(misans_regular, 20)
except:
    font_title = ImageFont.load_default()
    font_title2 = font_title
    font_sub = font_title

# 标题居中
bbox1 = draw.textbbox((0, 0), title, font=font_title)
tw1 = bbox1[2] - bbox1[0]
x1 = (900 - tw1) // 2
draw.text((x1, 320), title, font=font_title, fill=(255, 255, 255))

bbox2 = draw.textbbox((0, 0), title2, font=font_title2)
tw2 = bbox2[2] - bbox2[0]
x2 = (900 - tw2) // 2
draw.text((x2, 375), title2, font=font_title2, fill=(100, 200, 255))

# 副标题
sub = 'GitHub 6.8万星 | 52700+社区技能'
bbox3 = draw.textbbox((0, 0), sub, font=font_sub)
tw3 = bbox3[2] - bbox3[0]
x3 = (900 - tw3) // 2
draw.text((x3, 430), sub, font=font_sub, fill=(200, 200, 200))

# 保存
output = '/home/liyang/.openclaw/workspace/文章-OpenClaw经验分享_cover_final.jpg'
ai_img.save(output, quality=95)
print(f'Saved: {output}')
