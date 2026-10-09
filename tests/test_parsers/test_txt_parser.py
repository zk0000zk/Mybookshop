"""TxtParser 测试。"""
import os
import pytest

from src.parsers.txt_parser import TxtParser


class TestTxtParser:

    def test_parse_metadata(self, txt_file):
        """测试元数据解析。"""
        parser = TxtParser()
        metadata = parser.parse_metadata(txt_file)

        assert metadata.title == 'test_book'
        assert metadata.author is None
        assert metadata.file_format == 'txt'
        assert metadata.cover_path is None
        assert metadata.total_chapters == 1
        assert metadata.file_size > 0
        assert os.path.isabs(metadata.file_path)

    def test_parse_metadata_gbk(self, txt_file_gbk):
        """测试 GBK 编码文件的元数据解析。"""
        parser = TxtParser()
        metadata = parser.parse_metadata(txt_file_gbk)

        assert metadata.title == 'gbk_book'
        assert metadata.file_format == 'txt'

    def test_get_chapters(self, txt_file):
        """测试章节获取。"""
        parser = TxtParser()
        chapters = parser.get_chapters(txt_file)

        assert len(chapters) == 1
        assert chapters[0].index == 0
        assert chapters[0].title == '全文'
        assert '<p>' in chapters[0].content  # 应该转为 HTML
        assert chapters[0].is_html

    def test_get_chapter_content(self, txt_file):
        """测试获取章节内容。"""
        parser = TxtParser()
        content = parser.get_chapter_content(txt_file, 0)
        assert '测试文本' in content
        assert '<p>' in content

    def test_get_chapter_content_invalid_index(self, txt_file):
        """测试无效章节索引。"""
        parser = TxtParser()
        content = parser.get_chapter_content(txt_file, 999)
        assert content == ''

    def test_search_in_chapters(self, txt_file):
        """测试搜索功能。"""
        parser = TxtParser()
        results = parser.search_in_chapters(txt_file, 'mykeyword')

        assert len(results) == 2  # 出现了两次
        for r in results:
            assert r['chapter_index'] == 0
            assert r['chapter_title'] == '全文'
            assert 'mykeyword' in r['snippet'].lower()

    def test_search_no_match(self, txt_file):
        """测试搜索无匹配。"""
        parser = TxtParser()
        results = parser.search_in_chapters(txt_file, '不存在的关键词xyz123')
        assert len(results) == 0

    def test_get_chapters_gbk(self, txt_file_gbk):
        """测试 GBK 编码文件的章节获取。"""
        parser = TxtParser()
        chapters = parser.get_chapters(txt_file_gbk)
        assert len(chapters) == 1
        assert '中文文件' in chapters[0].content
