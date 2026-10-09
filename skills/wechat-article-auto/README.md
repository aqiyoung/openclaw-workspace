# 微信公众号自动化发布工具

一键完成：去AI化润色 → HTML美化 → 封面图生成 → 上传草稿箱

## 🚀 快速开始

```bash
# 基本使用
python scripts/publish_v2.py 文章.md

# 完整参数
python scripts/publish_v2.py 文章.md \
  --author "三页札记" \
  --style tech \
  --cover-style tech
```

## 📋 功能特性

- ✅ 去AI化润色（3种风格）
- ✅ HTML美化（微信兼容）
- ✅ 封面图生成（6种风格）
- ✅ 上传草稿箱
- ✅ 双字体方案
- ✅ 自动摘要提取

## 🎨 支持的风格

### 文章风格
- `tech` — 技术干货
- `story` — 故事叙事
- `opinion` — 观点评论

### 封面风格
- `tech` — 科技感 🚀
- `ocean` — 海洋风 🌊
- `sunset` — 日落 🌅
- `forest` — 森林 🌲
- `dark` — 暗黑 🌙
- `purple` — 紫韵 💜

## 📁 项目结构

```
wechat-article-auto/
├── SKILL.md              # 完整文档
├── README.md            # 本文件
├── config.json           # 配置文件
├── config/
│   └── config.json       # 配置文件（备用）
├── scripts/
│   ├── publish_v2.py     # 主脚本
│   ├── cover_generator.py        # 封面生成器
│   └── wechat_html_converter.py  # HTML转换器
├── tools/
│   ├── publish.py        # 旧版发布脚本
│   └── wechat_api.py     # 微信API工具
└── templates/
    └── article_template.html     # HTML模板
```

## ⚙️ 配置

编辑 `config.json`：

```json
{
  "wechat": {
    "app_id": "你的AppID",
    "app_secret": "你的AppSecret",
    "default_author": "你的名字"
  },
  "fonts": {
    "english": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "chinese": "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
  }
}
```

## 🔧 依赖

```bash
pip install pillow requests
```

## 📖 使用示例

### 技术文章
```bash
python scripts/publish_v2.py "AI助手在技术博客中的应用.md" \
  --style tech \
  --cover-style tech
```

### 故事文章
```bash
python scripts/publish_v2.py "一个程序员的成长故事.md" \
  --style story \
  --cover-style sunset
```

### 观点文章
```bash
python scripts/publish_v2.py "为什么我选择放弃大厂offer.md" \
  --style opinion \
  --cover-style dark
```

### 只生成封面
```bash
python scripts/publish_v2.py "文章.md" --cover-only --cover-style purple
```

### 跳过去AI化
```bash
python scripts/publish_v2.py "文章.md" --no-deai
```

## 📝 输出文件

- `文章_deai.md` — 去AI化后的文章
- `文章_html.txt` — 美化后的HTML
- `文章_cover.png` — 生成的封面图

## ⚠️ 注意事项

- 封面图必须使用双字体方案
- 首次使用前确保config.json已配置
- 去AI化处理会跳过代码块
- HTML美化后的文章可直接粘贴到微信公众号编辑器

## 🐛 故障排除

### 封面图生成失败
- 检查字体文件是否存在
- 检查字体路径是否正确
- 确保使用双字体方案

### 上传草稿箱失败
- 检查AppID和AppSecret是否正确
- 检查IP白名单是否配置
- 检查网络连接

## 📊 最佳实践

1. **选题阶段**：多角度分析，选择最有价值的切入点
2. **写作阶段**：保持原创性，避免抄袭
3. **润色阶段**：适度去AI化，保持专业性
4. **封面阶段**：选择与内容匹配的风格
5. **发布阶段**：选择最佳推送时间
6. **推送后**：关注数据反馈，优化后续内容

## 📞 支持

如有问题，请查看 SKILL.md。

---

**祝你创作愉快！** 🎉
