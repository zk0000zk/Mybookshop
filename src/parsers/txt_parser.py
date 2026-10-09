"""TXT 解析器：自动检测编码，整书作为单章节。"""
from __future__ import annotations

import os

from src.parsers.base_parser import BookMetadata, Chapter


class TxtParser:
    """TXT 文件解析器。"""

    @staticmethod
    def _detect_encoding(file_path: str) -> str:
        """使用 charset-normalizer 检测文件编码。"""
        from charset_normalizer import from_path

        result = from_path(file_path).best()
        if result and result.encoding:
            return result.encoding
        return 'utf-8'

    def parse_metadata(self, file_path: str) -> BookMetadata:
        title = os.path.splitext(os.path.basename(file_path))[0]
        file_size = os.path.getsize(file_path)

        return BookMetadata(
            title=title,
            author=None,
            file_path=os.path.abspath(file_path),
            file_format="txt",
            cover_path=None,
            total_chapters=1,
            file_size=file_size,
        )

    def get_chapters(self, file_path: str) -> list[Chapter]:
        encoding = self._detect_encoding(file_path)

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            text = f.read()

        # 将纯文本转为简单 HTML 段落
        html = self._text_to_html(text)

        return [Chapter(
            index=0,
            title="全文",
            content=html,
            is_html=True,
        )]

    def get_chapter_content(self, file_path: str, chapter_index: int) -> str:
        chapters = self.get_chapters(file_path)
        if chapters and chapter_index == 0:
            return chapters[0].content
        return ""

    @staticmethod
    def _text_to_html(text: str) -> str:
        """将纯文本转换为 HTML 段落，保留换行。"""
        import html as html_module

        escaped = html_module.escape(text)
        paragraphs = escaped.split('\n')
        html_parts = ['<div>']
        for para in paragraphs:
            if para.strip():
                html_parts.append(f'<p>{para.strip()}</p>')
            else:
                html_parts.append('<br/>')
        html_parts.append('</div>')
        return ''.join(html_parts)

    def search_in_chapters(self, file_path: str, keyword: str) -> list[dict]:
        """在 TXT 中搜索关键词。"""
        encoding = self._detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            text = f.read()

        results: list[dict] = []
        keyword_lower = keyword.lower()
        text_lower = text.lower()
        start = 0

        while True:
            pos = text_lower.find(keyword_lower, start)
            if pos == -1:
                break
            snippet_start = max(0, pos - 20)
            snippet_end = min(len(text), pos + len(keyword) + 20)
            snippet = text[snippet_start:snippet_end].replace('\n', ' ')
            results.append({
                'chapter_index': 0,
                'chapter_title': '全文',
                'snippet': snippet,
                'keyword': keyword,
            })
            start = pos + 1

        return results
