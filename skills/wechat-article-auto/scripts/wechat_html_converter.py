#!/usr/bin/env python3
# -*- coding: utf: utf-8 -*-
"""
微信HTML转换器
将Markdown转换为微信公众号兼容的HTML（纯HTML，样式由模板控制）
"""

import re
from pathlib import Path


def convert_inline_format(content):
    """处理行内格式：粗体、斜体、代码、链接、图片"""
    # 粗体
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', content)
    # 斜体
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    content = re.sub(r'_(.*?)_', r'<em>\1</em>', content)
    # 代码
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
    # 链接
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', content)
    # 图片
    content = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1">', content)
    return content


def convert_markdown_to_wechat(markdown_content):
    """将Markdown转换为微信公众号兼容的HTML（纯HTML，样式由模板控制）"""

    lines = markdown_content.split('\n')
    html_lines = []

    # 状态变量
    in_code_block = False
    in_list = False
    in_quote = False
    in_table = False
    code_lang = ''

    i = 0
    while i < len(lines):
        line = lines[i]

        # 代码块
        if line.strip().startswith('```'):
            if in_code_block:
                html_lines.append('</pre></div>')
                in_code_block = False
            else:
                code_lang = line.strip()[3:].strip()
                html_lines.append('<div class="code-block"><pre>')
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_lines.append(escaped_line)
            i += 1
            continue

        # 引用块
        if line.strip().startswith('>'):
            if not in_quote:
                html_lines.append('<blockquote>')
                in_quote = True
            content = line.strip()[1:].strip()
            html_lines.append(f'<p>{content}</p>')
            i += 1
            continue
        elif in_quote:
            html_lines.append('</blockquote>')
            in_quote = False

        # 表格检测：当前行是 | ... | ... |，且下一行是 |---|---|... |
        if (line.strip().startswith('|') and line.strip().endswith('|')
                and i + 1 < len(lines)
                and re.match(r'^\|[-\s|:]+\|$', lines[i + 1].strip())):
            # 跳过表头分隔行，开始表格
            in_table = True
            table_rows = [line]
            i += 2  # 跳过分隔行
            # 收集表格行
            while i < len(lines) and lines[i].strip().startswith('|') and lines[i].strip().endswith('|'):
                table_rows.append(lines[i])
                i += 1
            # 转换表格为 HTML
            html_lines.append('<table style="width:100%;border-collapse:collapse;margin:16px 0;">')
            for idx, row in enumerate(table_rows):
                cells = [c.strip() for c in row.strip().strip('|').split('|')]
                if idx == 0:
                    html_lines.append('<thead><tr>')
                    for cell in cells:
                        cell = convert_inline_format(cell)
                        html_lines.append(f'<th style="border:1px solid #ddd;padding:8px 12px;background:#f5f5f5;font-weight:600;">{cell}</th>')
                    html_lines.append('</tr></thead><tbody>')
                else:
                    html_lines.append('<tr>')
                    for cell in cells:
                        cell = convert_inline_format(cell)
                        html_lines.append(f'<td style="border:1px solid #ddd;padding:8px 12px;">{cell}</td>')
                    html_lines.append('</tr>')
            html_lines.append('</tbody></table>')
            in_table = False
            continue

        # 标题
        if line.startswith('###'):
            content = line.lstrip('#').strip()
            html_lines.append(f'<h3>{content}</h3>')
        elif line.startswith('##'):
            content = line.lstrip('#').strip()
            html_lines.append(f'<h2>{content}</h2>')
        elif line.startswith('#'):
            content = line.lstrip('#').strip()
            html_lines.append(f'<h1>{content}</h1>')
        # 无序列表
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                html_lines.append('<ul style="list-style:none;padding:0;margin:12px 0;">')
                in_list = True
            content = line.strip()[2:].strip()
            content = convert_inline_format(content)
            html_lines.append(f'<li style="padding:4px 0;font-size:17px;line-height:1.8;">{content}</li>')
        # 有序列表
        elif re.match(r'^\d+\.\s', line.strip()):
            if not in_list:
                html_lines.append('<ul style="list-style:none;padding:0;margin:12px 0;">')
                in_list = True
            content = re.sub(r'^\d+\.\s', '', line.strip())
            content = convert_inline_format(content)
            html_lines.append(f'<li style="padding:4px 0;font-size:17px;line-height:1.8;">{content}</li>')
        elif in_list and not line.strip():
            html_lines.append('</ul>')
            in_list = False
        # 分隔线
        elif line.strip() == '---' or line.strip() == '***':
            html_lines.append('<hr style="border:none;border-top:1px solid #eee;margin:24px 0;">')
        # 空行：跳过，不生成空 <p>
        elif not line.strip():
            if in_list:
                html_lines.append('</ul>')
                in_list = False
        # 普通段落
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            content = line.strip()
            # 自动识别小标题（以中文冒号结尾的短句）
            if content.endswith('：') and len(content) < 30:
                content = f'<strong>{content}</strong>'
            content = convert_inline_format(content)
            if content:
                html_lines.append(f'<p style="margin:0 0 16px 0;font-size:17px;line-height:1.9;color:#374151;">{content}</p>')

        i += 1

    # 结束未关闭的标签
    if in_list:
        html_lines.append('</ul>')
    if in_quote:
        html_lines.append('</blockquote>')

    html_content = '\n'.join(html_lines)
    return html_content


if __name__ == '__main__':
    test = """# 测试

这是一段文字。

## 标题

- 列表项1
- 列表项2

| 列1 | 列2 |
|---|---|
| a | b |

> 引用

**粗体** 和 `代码`
"""
    print(convert_markdown_to_wechat(test))
