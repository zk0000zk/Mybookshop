"""文本处理工具：搜索高亮等。"""
from __future__ import annotations

import html as html_module


def highlight_keyword(text: str, keyword: str) -> str:
    """在文本中高亮关键词（用于搜索结果显示）。"""
    if not keyword or not text:
        return html_module.escape(text or '')

    escaped_text = html_module.escape(text)
    escaped_keyword = html_module.escape(keyword)

    # 大小写不敏感替换
    lower_text = escaped_text.lower()
    lower_keyword = escaped_keyword.lower()

    result: list[str] = []
    start = 0
    while True:
        pos = lower_text.find(lower_keyword, start)
        if pos == -1:
            result.append(escaped_text[start:])
            break
        result.append(escaped_text[start:pos])
        result.append(f'<b style="background-color: #FFD700; color: #000;">{escaped_text[pos:pos + len(escaped_keyword)]}</b>')
        start = pos + len(escaped_keyword)

    return ''.join(result)
