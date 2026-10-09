#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
封面图生成器
支持多种风格，使用双字体方案
"""

import os
import json
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

class CoverGenerator:
    """封面图生成器"""
    
    # 风格配置
    STYLES = {
        "tech": {
            "bg_gradient": [(0, 30, 60), (0, 60, 120)],
            "accent_color": (255, 50, 50),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 100),
            "emoji": "🚀"
        },
        "ocean": {
            "bg_gradient": [(0, 60, 80), (0, 100, 120)],
            "accent_color": (0, 200, 255),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 100),
            "emoji": "🌊"
        },
        "sunset": {
            "bg_gradient": [(200, 80, 40), (255, 120, 60)],
            "accent_color": (255, 200, 0),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 100),
            "emoji": "🌅"
        },
        "forest": {
            "bg_gradient": [(0, 80, 40), (0, 120, 60)],
            "accent_color": (100, 255, 100),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 100),
            "emoji": "🌲"
        },
        "dark": {
            "bg_gradient": [(30, 30, 30), (60, 60, 60)],
            "accent_color": (255, 50, 50),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 150),
            "emoji": "🌙"
        },
        "purple": {
            "bg_gradient": [(80, 40, 120), (120, 60, 180)],
            "accent_color": (255, 200, 255),
            "text_color": (255, 255, 255),
            "shadow_color": (0, 0, 0, 100),
            "emoji": "💜"
        }
    }
    
    def __init__(self, config_path=None):
        """初始化"""
        self.width = 900
        self.height = 500
        
        # 加载配置
        self.config = self.load_config(config_path)
        
        # 优先使用MiSans字体（同时支持中英文）
        misans = self.config.get('fonts', {}).get('misans')
        misans_bold = self.config.get('fonts', {}).get('misans_bold')
        
        if misans and os.path.exists(misans):
            # 使用MiSans作为统一字体
            self.font_en = misans
            self.font_zh = misans_bold if (misans_bold and os.path.exists(misans_bold)) else misans
            self.use_misans = True
            print(f"[OK] 使用MiSans字体: {misans}")
        else:
            # 双字体方案（备用）
            self.font_en = self.config.get('fonts', {}).get('english', "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
            self.font_zh = self.config.get('fonts', {}).get('chinese', "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf")
            self.use_misans = False
        
        # 检查字体是否存在
        self.check_fonts()
    
    def load_config(self, config_path=None):
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 加载配置文件失败: {e}")
            return {}
    
    def check_fonts(self):
        """检查字体文件"""
        # 如果使用MiSans，只需检查MiSans字体
        if self.use_misans:
            if not os.path.exists(self.font_en):
                print(f"[ERROR] MiSans字体不存在: {self.font_en}")
            else:
                print(f"[OK] MiSans字体已就绪: {self.font_en}")
            return
        
        # 检查英文字体（双字体方案备用）
        if not os.path.exists(self.font_en):
            print(f"[WARN] 英文字体不存在: {self.font_en}")
            # 尝试其他字体
            fallback_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
            ]
            for font in fallback_fonts:
                if os.path.exists(font):
                    self.font_en = font
                    print(f"[OK] 使用备用英文字体: {font}")
                    break
        
        # 检查中文字体
        if not os.path.exists(self.font_zh):
            print(f"[WARN] 中文字体不存在: {self.font_zh}")
            # 尝试其他字体
            fallback_fonts = [
                "/usr/share/fonts/truetype/droid/DroidSansFallback.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
            ]
            for font in fallback_fonts:
                if os.path.exists(font):
                    self.font_zh = font
                    print(f"[OK] 使用备用中文字体: {font}")
                    break
    
    def create_gradient(self, width, height, colors):
        """创建渐变背景"""
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        for y in range(height):
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * y / height)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * y / height)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return image
    
    def add_decorations(self, draw, width, height, accent_color):
        """添加装饰元素"""
        # 随机几何图形
        for _ in range(5):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 80)
            shape = random.choice(['circle', 'rect'])
            
            if shape == 'circle':
                draw.ellipse([x, y, x + size, y + size], 
                            fill=(*accent_color, 50), outline=(*accent_color, 100))
            else:
                draw.rectangle([x, y, x + size, y + size], 
                              fill=(*accent_color, 50), outline=(*accent_color, 100))
        
        # 角落装饰
        corner_size = 100
        draw.rectangle([0, 0, corner_size, 10], fill=accent_color)
        draw.rectangle([0, 0, 10, corner_size], fill=accent_color)
        draw.rectangle([width - corner_size, height - 10, width, height], fill=accent_color)
        draw.rectangle([width - 10, height - corner_size, width, height], fill=accent_color)
    
    def add_brand_logos_pil(self, image, width, height):
        """在标题上方添加三个品牌logo，统一高度，等比宽"""
        logo_dir = Path(__file__).parent.parent / "tools" / "brand_logos"
        logo_files = ["openai_clean.png", "deepseek_clean.png", "xiaomi_clean.png"]
        
        # 统一高度，宽度等比缩放，保持logo本身比例
        desired_height = 160
        logos = []
        total_logo_w = 0
        for fname in logo_files:
            path = logo_dir / fname
            if path.exists():
                try:
                    img = Image.open(path).convert("RGBA")
                    w, h = img.size
                    scale = desired_height / h
                    new_w = int(w * scale)
                    img = img.resize((new_w, desired_height), Image.LANCZOS)
                    logos.append(img)
                    total_logo_w += new_w
                except Exception as e:
                    print(f"[WARN] 加载logo {path} 失败: {e}")
        
        if len(logos) < 3:
            return
        
        # 水平排列，自适应间距
        spacing = 30
        total_w = total_logo_w + (len(logos)-1) * spacing
        
        # 如果太宽，等比缩小间距或整体缩放
        if total_w > width - 40:
            scale = (width - 40) / total_w
            desired_height = int(desired_height * scale)
            spacing = 20
            # 重新缩放
            logos = []
            total_logo_w = 0
            for fname in logo_files:
                path = logo_dir / fname
                if path.exists():
                    try:
                        img = Image.open(path).convert("RGBA")
                        w, h = img.size
                        scale = desired_height / h
                        new_w = int(w * scale)
                        img = img.resize((new_w, desired_height), Image.LANCZOS)
                        logos.append(img)
                        total_logo_w += new_w
                    except:
                        pass
            total_w = total_logo_w + (len(logos)-1) * spacing
        
        start_x = (width - total_w) // 2
        logo_y = 60  # 顶部边距
        
        paste_x = start_x
        for logo in logos:
            r, g, b, a = logo.split()
            a = a.point(lambda x: min(int(x * 0.85), 220))
            logo_alpha = Image.merge('RGBA', (r, g, b, a))
            image.paste(logo_alpha, (paste_x, logo_y), logo_alpha)
            paste_x += logo.size[0] + spacing
    
    def draw_text(self, draw, text, width, height, style):
        """绘制文字（MiSans统一字体 / 双字体备用）"""
        # 使用MiSans时，不再分离中英文（MiSans同时支持中英文）
        if self.use_misans:
            base_font_size = 48
            try:
                font = ImageFont.truetype(self.font_zh, base_font_size)  # MiSans-Bold优先
            except Exception as e:
                print(f"[ERROR] 加载MiSans字体失败: {e}")
                return
            
            # 计算文本宽度
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 调整字体大小以适应宽度
            max_width = width - 200
            if text_width > max_width:
                scale = max_width / text_width
                new_size = int(base_font_size * scale)
                font = ImageFont.truetype(self.font_zh, new_size)
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            
            # 计算位置
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # 绘制阴影
            shadow_offset = 3
            shadow_color = style["shadow_color"]
            draw.text((x + shadow_offset, y + shadow_offset), text, 
                     font=font, fill=shadow_color)
            draw.text((x, y), text, font=font, fill=style["text_color"])
        else:
            # 双字体方案（备用）
            en_text = ""
            zh_text = ""
            
            for char in text:
                if '\u4e00' <= char <= '\u9fff':
                    zh_text += char
                else:
                    en_text += char
            
            # 计算字体大小
            base_font_size = 48
            en_font_size = base_font_size
            zh_font_size = base_font_size
            
            # 加载字体
            try:
                font_en = ImageFont.truetype(self.font_en, en_font_size)
                font_zh = ImageFont.truetype(self.font_zh, zh_font_size)
            except Exception as e:
                print(f"[ERROR] 加载字体失败: {e}")
                return
            
            # 计算文本宽度
            en_bbox = draw.textbbox((0, 0), en_text, font=font_en)
            zh_bbox = draw.textbbox((0, 0), zh_text, font=font_zh)
            
            en_width = en_bbox[2] - en_bbox[0]
            zh_width = zh_bbox[2] - zh_bbox[0]
            total_width = en_width + zh_width
            
            # 调整字体大小以适应宽度
            max_width = width - 200
            if total_width > max_width:
                scale = max_width / total_width
                en_font_size = int(en_font_size * scale)
                zh_font_size = int(zh_font_size * scale)
                font_en = ImageFont.truetype(self.font_en, en_font_size)
                font_zh = ImageFont.truetype(self.font_zh, zh_font_size)
            
            # 重新计算宽度
            en_bbox = draw.textbbox((0, 0), en_text, font=font_en)
            zh_bbox = draw.textbbox((0, 0), zh_text, font=font_zh)
            en_width = en_bbox[2] - en_bbox[0]
            zh_width = zh_bbox[2] - zh_bbox[0]
            
            # 计算位置
            total_width = en_width + zh_width
            x = (width - total_width) // 2
            y = (height - max(en_font_size, zh_font_size)) // 2
            
            # 绘制阴影
            shadow_offset = 3
            shadow_color = style["shadow_color"]
            
            if en_text:
                draw.text((x + shadow_offset, y + shadow_offset), en_text, 
                         font=font_en, fill=shadow_color)
                draw.text((x, y), en_text, font=font_en, fill=style["text_color"])
                x += en_width
            
            if zh_text:
                draw.text((x + shadow_offset, y + shadow_offset), zh_text, 
                         font=font_zh, fill=shadow_color)
                draw.text((x, y), zh_text, font=font_zh, fill=style["text_color"])
    
    def generate(self, title, output_path, style="tech", author=None):
        """生成封面图"""
        print(f"[START] 生成封面图: {title}")
        
        # 获取风格配置
        style_config = self.STYLES.get(style, self.STYLES["tech"])
        
        # 创建渐变背景
        image = self.create_gradient(self.width, self.height, style_config["bg_gradient"])
        draw = ImageDraw.Draw(image, 'RGBA')
        
        # 添加装饰
        self.add_decorations(draw, self.width, self.height, style_config["accent_color"])
        
        # 添加品牌logo水印（标题后方）
        self.add_brand_logos_pil(image, self.width, self.height)
        
        # 绘制文字
        self.draw_text(draw, title, self.width, self.height, style_config)
        
        # 添加作者信息
        if author:
            try:
                author_font = ImageFont.truetype(self.font_zh, 24)
                draw.text((20, self.height - 40), f"作者: {author}", 
                         font=author_font, fill=(255, 255, 255, 200))
            except Exception as e:
                print(f"[WARN] 添加作者信息失败: {e}")
        
        # 保存图片
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path, 'PNG')
        
        print(f"[OK] 封面图已保存: {output_path}")
        return {"success": True, "path": str(output_path)}


if __name__ == '__main__':
    # 测试
    generator = CoverGenerator()
    generator.generate(
        title="AI助手在技术博客中的应用",
        output_path="/tmp/test_cover_misans.png",
        style="tech",
        author="三页札记"
    )
    print("[DONE] 测试完成！")
