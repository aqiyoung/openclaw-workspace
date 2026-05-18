# WeChat Publishing Guidelines

## Article Requirements
- **Author**: 三页札记
- **Copyright**: Must mark as original content
- **Body Format**: No max-width restriction
- **Code Blocks**: Use `<pre style="..."><code>...</code></pre>`

## Code Block Styling Template
```html
<pre style="background: #0d1117; color: #e6edf3; padding: 14px 18px; border-radius: 8px; font-family: Menlo, Consolas, monospace; font-size: 14px; line-height: 1.6; overflow-x: auto; margin: 10px 0; border: 1px solid #30363d; white-space: pre-wrap; word-break: break-all;"><code>
代码内容
</code></pre>
```

## Cover Image Generation
- **Preferred Tool**: `scripts/cover_gen.py` (PIL + Noto SC font)
- **Dimensions**: 900x383 (horizontal for WeChat)
- **Styles**: Deep blue tech, deep green, yellow-black warning, white background
- **Avoid**: AI-generated images (wrong aspect ratio, watermarks)

## IP Whitelist Management
- **AppID**: wx97bc84bb54232e27
- **Current IP**: 111.19.39.227
- **Action Required**: Notify boss when IP changes (error 40164)