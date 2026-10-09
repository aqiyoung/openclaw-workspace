---
name: wechat-article-auto
description: 微信公众号文章自动化发布。一键完成：去AI化润色 → HTML转换 → 封面图生成(含品牌logo) → 上传草稿箱。
version: 3.2.0
last_updated: 2026-04-29
---

# 微信公众号自动化发布工具

一键完成：**去AI化润色(可选)** → **HTML美化(现代化排版)** → **封面图生成(含品牌logo)** → **上传草稿箱**

## 🎨 AI 生图（ModelScope Z-Image-Turbo）

公众号文章配图可以使用 AI 生成，免费使用。

### 使用方式
```bash
python3 ~/.openclaw/workspace/skills/imgforge/imgforge.py "图片描述" -o 输出路径.jpg
```

### 示例
```bash
# 生成技术风配图
python3 ~/.openclaw/workspace/skills/imgforge/imgforge.py "一只可爱的橘猫在阳光下睡觉" -o /tmp/cat.jpg

# 指定尺寸
python3 ~/.openclaw/workspace/skills/imgforge/imgforge.py "未来科技城市" -o /tmp/city.jpg -W 1280 -H 720
```

### 限制
- 每天免费额度：500,000 tokens（约 1000-2500 张图）
- 建议每张图间隔 3-5 秒，避免限流
- 需要 MODELSCOPE_API_KEY 环境变量（已配置）

### 依赖
- Python 3 + Pillow
- ModelScope API Key（环境变量 MODELSCOPE_API_KEY）

## 🎨 现代化排版（Notion/Typora风格）

### 标题字号
- h1: 32px，700字重，纯黑色
- h2: 26px，600字重，纯黑色
- h3: 22px，600字重，纯黑色

### 正文样式
- 字号：17px
- 行高：1.9
- 段落间距：40px（明显空行）
- 颜色：#374151（深灰）

### 粗体
- 字重：700
- 字号：18px
- 颜色：纯黑色
- **自动识别小标题**：以中文冒号结尾的短句（如"核心亮点："）自动加粗

### 代码块
- 背景：深色 #1f2937
- 文字：浅灰 #e5e7eb
- 圆角：8px
- 内边距：20px

### 引用块
- 背景：浅灰 #f9fafb
- 左边框：4px #d1d5db
- 右上圆角：8px

### 链接
- 颜色：蓝色 #2563eb
- Hover：下划线

### 图片
- 圆角：8px
- 阴影：0 2px 8px rgba(0,0,0,0.1)

## 🚀 快速使用

**默认就是干净模式。** 无需加任何额外参数。

```bash
# 最简洁方式（推荐）：无AI去味、无模板装饰、封面无作者
python scripts/publish_v2.py 文章.md --author "三页札记"

# 指定封面风格
python scripts/publish_v2.py 文章.md --cover-style purple --author "三页札记"

# 需要去AI化
python scripts/publish_v2.py 文章.md --deai --author "三页札记"

# 需要模板装饰（头部底部有图标）
python scripts/publish_v2.py 文章.md --with-meta --author "三页札记"
```

## 📋 全部参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `article` | Markdown文件路径 | 必填 |
| `--author` | 作者名 | config默认值 |
| `--digest` | 摘要（不传自动从md正文安全提取） | 自动 |
| `--deai` | 开启AI去味润色（默认关闭） | 关闭 |
| `--with-meta` | 开启模板头部/底部装饰（默认关闭） | 关闭 |
| `--no-cover` | 跳过封面生成 | 否 |
| `--cover-only` | 只生成封面 | 否 |
| `--cover-style` | 封面风格：tech/ocean/sunset/forest/dark/purple | tech |

## 🔥 最佳实践（踩坑总结）

### ⚠️ 第一条：默认已关闭去AI化（不用加参数）
去AI化会随机添加口语化标签如 `（真香）`、`（踩过坑的都懂）`，已默认关闭。
**需要时主动加 `--deai`**

### ⚠️ 第二条：默认无装饰（不用加参数）
模板装饰（`✍️ 📅⏱️👀`、`✨💫⭐`、`© 版权`、`点赞收藏分享`）已默认关闭。
**需要时主动加 `--with-meta`**

### ⚠️ 第三条：摘要从 Markdown 正文提取
`create_draft` 的摘要不能从 HTML 内容提取，因为 HTML 开头有 `<style>` 块，提取出来会变成 CSS 乱码。
**修复：** `process_article` 中在 markdown 阶段预生成摘要，传入 `create_draft`。

### ⚠️ 第四条：封面图用 MiSans 字体，不用双字体
MiSans 中英混合渲染效果极佳，无需 DroidSans + DejaVu 双字体方案。

### ⚠️ 第五条：封面品牌 logo
需要老板提供真实 logo 图片（存放在 `tools/brand_logos/` 目录），默认用三个透明背景 PNG：
- `openai_clean.png` — OpenAI logo
- `deepseek_clean.png` — DeepSeek logo
- `xiaomi_clean.png` — 小米 logo

去背景规则：采样四角颜色作为背景色，阈值 50 以内设为透明。

### ⚠️ 第六条：标题长度限制
微信标题限制 **64字节（UTF-8）**，不是 64 个字符。中文标题一般只能放 20 个字左右。

### ⚠️ 第七条：作者名长度限制
微信作者名限制 **8字节**，中文相当于 2 个汉字加空格都危险。脚本会自动截断。

### ⚠️ 第八条：JSON 中文转义
`json.dumps` 必须加 `ensure_ascii=False`，否则中文变成 `\uXXXX` 乱码。

### ⚠️ 第九条：正文不要用相对时间词
公众号不是实时发布的（可能今天写好明天发），`"昨天"`、`"今天"`、`"前两天"` 这类词在正文和标题中都要避免。
**用绝对日期：** `"4月24日"` 永远比 `"昨天"` 安全。

### ⚠️ 第十条：不要用无序列表符号
微信公众号排版中，markdown 的 `-` 列表转 HTML 后段落间有额外间距。**用空行分隔的纯段落**代替列表。

## 🖼️ 封面风格

| 风格 | 代码 | 特点 |
|------|------|------|
| 科技感 | `tech` | 深蓝渐变 + 红色点缀 |
| 海洋风 | `ocean` | 蓝绿渐变 + 青色点缀 |
| 日落 | `sunset` | 橙红渐变 + 金色点缀 |
| 森林 | `forest` | 绿色渐变 + 浅绿点缀 |
| 暗黑 | `dark` | 深灰渐变 + 红色点缀 |
| 紫韵 | `purple` | 紫色渐变 + 金色点缀 |

封面图自动添加品牌 logo（浮在标题上方），使用 `tools/brand_logos/` 下的图片。

## 📁 输出文件

在文章同目录下生成：
- `文章_html.txt` — 转换后的 HTML（可直接粘贴进微信编辑器）
- `文章_cover.png` — 封面图
- `文章_deai.md` — 去AI化后的 md（仅在加 `--deai` 时生成）

## ⚙️ 配置文件

`config/config.json`：

```json
{
  "wechat": {
    "app_id": "wx97bc84bb54232e27",
    "app_secret": "31dd5e8ce9bf116d1b5ca3b81c2d82ea",
    "default_author": "三页札记",
    "ip_whitelist": "111.19.38.90"
  }
}
```

## 🔧 文件结构

```
skills/wechat-article-auto/
├── SKILL.md                    # 本文档
├── config/
│   └── config.json             # 微信API配置
├── scripts/
│   ├── publish_v2.py           # 主入口脚本
│   ├── wechat_html_converter.py # Markdown → HTML转换
│   └── cover_generator.py      # 封面图生成（含品牌logo）
├── templates/
│   ├── article_template.html    # 简洁模板（无装饰，新版本）
│   └── article_template_default.html  # 原模板备份（带装饰）
├── tools/
│   └── brand_logos/
│       ├── openai_clean.png     # OpenAI logo(去背景)
│       ├── deepseek_clean.png   # DeepSeek logo(去背景)
│       └── xiaomi_clean.png     # 小米 logo(去背景)
```

## 🎨 文章内容规范

### 标题
- 不用相对时间词（昨天/今天/明天）
- 控制在 20 字以内（64字节限制）
- 有吸引力但不标题党

### 正文
- 不用无列表符号（`-`、`·`），用空行分隔的纯段落
- 时间用绝对日期（4月24日）
- 避免 AI 痕迹词：首先/其次/最后/综上所述/不可否认
- 不用口语化标签：（真香）（踩过坑的都懂）
- 不用装饰性分割线（`---`）
- 不用版权声明（© 2026）、底部装饰符号

### 示例命令
```bash
# 明天要发布的文章（默认就是干净模式）：
python scripts/publish_v2.py 文章.md --cover-style purple --author "三页札记"
```

## 📝 发布检查清单

发布前确认：
- [ ] 标题无相对时间词
- [ ] 正文无相对时间词
- [ ] 无 `---` 分割线
- [ ] 无 `© 版权` 声明
- [ ] 无 `感谢阅读`、`点赞收藏分享`
- [ ] 无 `✍️ 📅 ⏱️ 👀` 装饰
- [ ] 无 `✨ 💫 ⭐ 🌟` 装饰
- [ ] 无 `（真香）` `（踩过坑的都懂）` 标签
- [ ] 摘要显示正常（不是CSS乱码）
- [ ] 封面图无作者文字（默认）
- [ ] 封面 logo 显示正常

## 依赖

- Python 3.6+
- Pillow（封面图生成）
- requests（微信API调用）
- MiSans 字体（封面字）
