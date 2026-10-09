"""EpubParser 测试。
使用 conftest.py 中的 mini_epub fixture。
"""
import os
import pytest

from src.parsers.epub_parser import EpubParser


class TestEpubParser:

    def test_parse_metadata(self, mini_epub):
        """测试 EPUB 元数据解析。"""
        parser = EpubParser()
        metadata = parser.parse_metadata(mini_epub)

        assert metadata.title == '测试电子书'
        assert metadata.author == '测试作者'
        assert metadata.file_format == 'epub'
        assert metadata.total_chapters == 2
        assert metadata.file_size > 0

    def test_get_chapters(self, mini_epub):
        """测试 EPUB 章节获取。"""
        parser = EpubParser()
        chapters = parser.get_chapters(mini_epub)

        assert len(chapters) == 2
        assert chapters[0].index == 0
        assert chapters[1].index == 1
        assert '开始' in chapters[0].title or '第一章' in chapters[0].title
        assert '继续' in chapters[1].title or '第二章' in chapters[1].title
        assert chapters[0].is_html

    def test_get_chapter_content(self, mini_epub):
        """测试获取单个章节内容。"""
        parser = EpubParser()
        content = parser.get_chapter_content(mini_epub, 0)
        assert '第一章' in content

        content2 = parser.get_chapter_content(mini_epub, 1)
        assert '第二章' in content2

    def test_get_chapter_content_invalid_index(self, mini_epub):
        """测试无效章节索引。"""
        parser = EpubParser()
        content = parser.get_chapter_content(mini_epub, 999)
        assert content == ''

    def test_search_in_chapters(self, mini_epub):
        """测试 EPUB 搜索功能。"""
        parser = EpubParser()
        results = parser.search_in_chapters(mini_epub, 'mykeyword')

        assert len(results) == 2  # 两章各出现一次
        chapter_indices = {r['chapter_index'] for r in results}
        assert chapter_indices == {0, 1}

    def test_search_no_match(self, mini_epub):
        """测试搜索无匹配。"""
        parser = EpubParser()
        results = parser.search_in_chapters(mini_epub, '不存在的关键词xyz')
        assert len(results) == 0

    def test_chapter_title_extraction(self, mini_epub):
        """测试章节标题提取。"""
        parser = EpubParser()
        chapters = parser.get_chapters(mini_epub)
        # 第一章用 h1 标题
        assert '开始' in chapters[0].title
        # 第二章用 h2 标题
        assert '继续' in chapters[1].title

    def test_html_cleanup(self):
        """测试 HTML 清理功能。"""
        parser = EpubParser()
        dirty_html = '<script>alert("xss")</script><style>body{}</style><p>text</p>'
        clean = parser._clean_html(dirty_html)

        assert '<script>' not in clean.lower()
        assert '<style>' not in clean.lower()
        assert '<p>text</p>' in clean
