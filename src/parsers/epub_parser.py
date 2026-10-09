"""EPUB 解析器：使用 EbookLib 读取 OPF/NCX，提取章节 HTML 和元数据。"""
from __future__ import annotations

import os
import tempfile
import hashlib

from src.parsers.base_parser import BookMetadata, Chapter


class EpubParser:
    """使用 EbookLib 解析 EPUB 文件。"""

    # ---------- 简单 HTML 清理 ----------
    @staticmethod
    def _clean_html(html: str) -> str:
        """移除 script/style 标签和 EPUB 特有命名空间前缀。"""
        import re
        # 移除 <script> 和 <style> 块
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # 清理 epub 命名空间
        html = html.replace('epub:type', 'data-epub-type')
        html = html.replace('epib:', '')
        return html

    @staticmethod
    def _html_to_plain_text(html: str) -> str:
        """简单将 HTML 转为纯文本（用于搜索）。"""
        import re
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # ---------- 元数据解析 ----------
    def parse_metadata(self, file_path: str) -> BookMetadata:
        from ebooklib import epub, ITEM_COVER

        book = epub.read_epub(file_path, options={'ignore_ncx': False})

        # 标题
        title = self._get_metadata_field(book, 'DC:title') or os.path.splitext(os.path.basename(file_path))[0]

        # 作者
        author = self._get_metadata_field(book, 'DC:creator')

        # 封面
        cover_path = self._extract_cover(book, file_path)

        # 章节数
        chapters = [item for item in book.spine if item[0] is not None]
        total_chapters = len(chapters) if chapters else 0

        file_size = os.path.getsize(file_path)

        return BookMetadata(
            title=title,
            author=author,
            file_path=os.path.abspath(file_path),
            file_format="epub",
            cover_path=cover_path,
            total_chapters=total_chapters,
            file_size=file_size,
        )

    @staticmethod
    def _get_metadata_field(book, field_name: str) -> str | None:
        """安全地从 EPUB 元数据中获取字段。"""
        try:
            values = book.get_metadata('DC', field_name.replace('DC:', ''))
            if values:
                # (value, attrs) 元组
                return values[0][0]
        except Exception:
            pass
        return None

    def _extract_cover(self, book, epub_path: str) -> str | None:
        """提取封面图片到临时目录。"""
        from ebooklib import epub, ITEM_COVER

        try:
            for item in book.get_items_of_type(ITEM_COVER):
                cover_bytes = item.get_content()
                if cover_bytes:
                    return self._save_cover_image(cover_bytes, epub_path, item.get_name())
        except Exception:
            pass

        # fallback：尝试从 manifest 中找 id 含 cover 的图片
        try:
            for item in book.get_items():
                name_lower = (item.get_name() or '').lower()
                item_id = (item.get_id() or '').lower()
                if 'cover' in name_lower or 'cover' in item_id:
                    if item.media_type and item.media_type.startswith('image'):
                        cover_bytes = item.get_content()
                        if cover_bytes:
                            return self._save_cover_image(cover_bytes, epub_path, item.get_name())
        except Exception:
            pass

        return None

    @staticmethod
    def _save_cover_image(data: bytes, epub_path: str, name: str) -> str:
        """将封面数据保存到临时目录，返回路径。"""
        # 用 epub 路径 hash 做唯一前缀
        path_hash = hashlib.md5(os.path.abspath(epub_path).encode()).hexdigest()[:12]
        ext = os.path.splitext(name)[1] or '.jpg'
        cover_dir = os.path.join(tempfile.gettempdir(), 'mybookshelf_covers')
        os.makedirs(cover_dir, exist_ok=True)
        cover_file = os.path.join(cover_dir, f'{path_hash}{ext}')
        with open(cover_file, 'wb') as f:
            f.write(data)
        return cover_file

    # ---------- 章节获取 ----------
    def get_chapters(self, file_path: str) -> list[Chapter]:
        from ebooklib import epub

        book = epub.read_epub(file_path, options={'ignore_ncx': False})
        chapters: list[Chapter] = []

        for idx, (spine_entry, _linear) in enumerate(book.spine):
            # EbookLib spine 条目可能是字符串 ID 或带 .id 属性的对象
            if spine_entry is None:
                continue
            if isinstance(spine_entry, str):
                item_id = spine_entry
            else:
                item_id = getattr(spine_entry, 'id', str(spine_entry))

            item = book.get_item_with_id(item_id)
            if item is None:
                continue

            html_content = item.get_content().decode('utf-8', errors='replace')
            html_content = self._clean_html(html_content)

            title = self._extract_chapter_title(html_content, idx)

            chapters.append(Chapter(
                index=idx,
                title=title,
                content=html_content,
                is_html=True,
            ))

        return chapters

    def get_chapter_content(self, file_path: str, chapter_index: int) -> str:
        """获取单个章节的渲染内容。"""
        chapters = self.get_chapters(file_path)
        if 0 <= chapter_index < len(chapters):
            return chapters[chapter_index].content
        return ""

    @staticmethod
    def _extract_chapter_title(html: str, fallback_idx: int) -> str:
        """从 HTML 中提取章节标题。"""
        import re
        match = re.search(r'<h[1-3][^>]*>(.*?)</h[1-3]>', html, re.IGNORECASE | re.DOTALL)
        if match:
            # 去掉内嵌标签
            title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            if title:
                return title
        return f'第 {fallback_idx + 1} 节'

    # ---------- 搜索辅助 ----------
    def search_in_chapters(self, file_path: str, keyword: str) -> list[dict]:
        """在所有章节中搜索关键词，返回匹配结果。"""
        results: list[dict] = []
        chapters = self.get_chapters(file_path)
        keyword_lower = keyword.lower()

        for ch in chapters:
            text = self._html_to_plain_text(ch.content)
            start = 0
            while True:
                pos = text.lower().find(keyword_lower, start)
                if pos == -1:
                    break
                # 取上下文片段
                snippet_start = max(0, pos - 20)
                snippet_end = min(len(text), pos + len(keyword) + 20)
                snippet = text[snippet_start:snippet_end]
                results.append({
                    'chapter_index': ch.index,
                    'chapter_title': ch.title,
                    'snippet': snippet,
                    'keyword': keyword,
                })
                start = pos + 1

        return results
