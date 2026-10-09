"""BookRepository 测试。"""
import os
import pytest

from src.repository.database import Database
from src.repository.book_repository import BookRepository


@pytest.fixture
def book_repo(temp_db):
    return BookRepository(temp_db)


class TestBookRepository:

    def test_add_and_get(self, book_repo):
        """测试添加并获取书籍。"""
        book_id = book_repo.add(
            title='测试书',
            author='作者',
            file_path='/tmp/test.epub',
            file_format='epub',
            cover_path=None,
            total_chapters=10,
            file_size=1024,
        )
        assert book_id > 0

        book = book_repo.get_by_id(book_id)
        assert book is not None
        assert book.title == '测试书'
        assert book.author == '作者'
        assert book.file_format == 'epub'
        assert book.total_chapters == 10

    def test_get_nonexistent(self, book_repo):
        """测试获取不存在的书籍。"""
        book = book_repo.get_by_id(999)
        assert book is None

    def test_list_all(self, book_repo):
        """测试列表查询。"""
        book_repo.add('书A', None, '/path/a.txt', 'txt', None, 1, 100)
        book_repo.add('书B', '作者B', '/path/b.epub', 'epub', None, 5, 200)

        books = book_repo.list_all()
        assert len(books) == 2

    def test_list_all_ordered(self, book_repo):
        """测试列表按最近阅读时间排序。"""
        id_a = book_repo.add('书A', None, '/path/a.txt', 'txt', None, 1, 100)
        id_b = book_repo.add('书B', None, '/path/b.txt', 'txt', None, 1, 100)

        # 只更新 B 的阅读时间
        book_repo.update_last_read_time(id_b)

        books = book_repo.list_all()
        # B 最近读过，应该在前面
        assert books[0].id == id_b
        assert books[1].id == id_a

    def test_delete(self, book_repo):
        """测试删除书籍。"""
        book_id = book_repo.add('书', None, '/path/test.txt', 'txt', None, 1, 100)
        assert book_repo.get_by_id(book_id) is not None

        book_repo.delete(book_id)
        assert book_repo.get_by_id(book_id) is None

    def test_update_last_read_time(self, book_repo):
        """测试更新最近阅读时间。"""
        book_id = book_repo.add('书', None, '/path/test.txt', 'txt', None, 1, 100)

        book = book_repo.get_by_id(book_id)
        assert book.last_read_at is None

        book_repo.update_last_read_time(book_id)

        book = book_repo.get_by_id(book_id)
        assert book.last_read_at is not None

    def test_check_file_exists_true(self, book_repo, tmp_path):
        """测试文件存在检查。"""
        test_file = tmp_path / 'exists.txt'
        test_file.write_text('content', encoding='utf-8')

        book_id = book_repo.add('书', None, str(test_file), 'txt', None, 1, 100)
        assert book_repo.check_file_exists(book_id) is True

    def test_check_file_exists_false(self, book_repo):
        """测试文件不存在检查。"""
        book_id = book_repo.add('书', None, '/nonexistent/path.txt', 'txt', None, 1, 100)
        assert book_repo.check_file_exists(book_id) is False
