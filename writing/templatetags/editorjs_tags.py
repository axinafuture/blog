import json
import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter(name='editorjs_render')
def editorjs_render(value):
    """Editor.js JSON 데이터를 HTML로 변환"""
    if not value:
        return ''

    try:
        data = json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return escape(value)

    blocks = data.get('blocks', [])
    html_parts = []

    for block in blocks:
        block_type = block.get('type')
        block_data = block.get('data', {})

        if block_type == 'paragraph':
            text = block_data.get('text', '')
            html_parts.append(f'<p>{text}</p>')

        elif block_type == 'header':
            text = block_data.get('text', '')
            level = block_data.get('level', 2)
            html_parts.append(f'<h{level}>{text}</h{level}>')

        elif block_type == 'list':
            style = block_data.get('style', 'unordered')
            items = block_data.get('items', [])
            tag = 'ol' if style == 'ordered' else 'ul'
            li_items = ''.join(f'<li>{item}</li>' for item in items)
            html_parts.append(f'<{tag}>{li_items}</{tag}>')

        elif block_type == 'checklist':
            items = block_data.get('items', [])
            checklist_html = '<div class="article-checklist">'
            for item in items:
                checked = 'checked' if item.get('checked') else ''
                text = item.get('text', '')
                checklist_html += f'<div class="article-checklist-item"><input type="checkbox" disabled {checked}> {text}</div>'
            checklist_html += '</div>'
            html_parts.append(checklist_html)

        elif block_type == 'image':
            url = block_data.get('file', {}).get('url', '')
            caption = block_data.get('caption', '')
            stretched = 'stretched' if block_data.get('stretched') else ''
            bordered = 'bordered' if block_data.get('withBorder') else ''
            bg = 'with-bg' if block_data.get('withBackground') else ''
            classes = ' '.join(filter(None, [stretched, bordered, bg]))
            img_html = f'<figure class="article-image {classes}">'
            img_html += f'<img src="{escape(url)}" alt="{escape(caption)}">'
            if caption:
                img_html += f'<figcaption>{caption}</figcaption>'
            img_html += '</figure>'
            html_parts.append(img_html)

        elif block_type == 'table':
            content = block_data.get('content', [])
            with_headings = block_data.get('withHeadings', False)
            table_html = '<table class="article-table">'
            for i, row in enumerate(content):
                if i == 0 and with_headings:
                    table_html += '<thead><tr>'
                    table_html += ''.join(f'<th>{cell}</th>' for cell in row)
                    table_html += '</tr></thead><tbody>'
                else:
                    table_html += '<tr>'
                    table_html += ''.join(f'<td>{cell}</td>' for cell in row)
                    table_html += '</tr>'
            if with_headings and len(content) > 1:
                table_html += '</tbody>'
            table_html += '</table>'
            html_parts.append(table_html)

        elif block_type == 'quote':
            text = block_data.get('text', '')
            caption = block_data.get('caption', '')
            quote_html = f'<blockquote><p>{text}</p>'
            if caption:
                quote_html += f'<cite>{caption}</cite>'
            quote_html += '</blockquote>'
            html_parts.append(quote_html)

        elif block_type == 'code':
            code = escape(block_data.get('code', ''))
            html_parts.append(f'<pre><code>{code}</code></pre>')

        elif block_type == 'delimiter':
            html_parts.append('<hr>')

        elif block_type == 'embed':
            service = block_data.get('service', '')
            embed_url = block_data.get('embed', '')
            caption = block_data.get('caption', '')
            html_parts.append(
                f'<div class="article-embed"><iframe src="{escape(embed_url)}" frameborder="0" allowfullscreen></iframe>'
                f'{"<p>" + caption + "</p>" if caption else ""}</div>'
            )

    return mark_safe('\n'.join(html_parts))


@register.filter(name='editorjs_plaintext')
def editorjs_plaintext(value):
    """Editor.js JSON 데이터에서 텍스트만 추출"""
    if not value:
        return ''

    try:
        data = json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return value

    texts = []
    for block in data.get('blocks', []):
        d = block.get('data', {})
        bt = block.get('type')
        if bt in ('paragraph', 'header', 'quote'):
            raw = d.get('text', '')
            texts.append(re.sub(r'<[^>]+>', '', raw))
        elif bt == 'list':
            for item in d.get('items', []):
                texts.append(re.sub(r'<[^>]+>', '', item))
        elif bt == 'checklist':
            for item in d.get('items', []):
                texts.append(re.sub(r'<[^>]+>', '', item.get('text', '')))
        elif bt == 'code':
            texts.append(d.get('code', ''))

    return ' '.join(texts)
