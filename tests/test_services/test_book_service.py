"""BookService 测试。"""
import pytest
import os

from src.repository.database import Database
from src.repository.book_repository import BookRepository
from src.services.book_service import BookService


@pytest.fixture
def book_service(temp_db):
    book_repo = BookRepository(temp_db)
    return BookService(book_repo)


class TestBookService:

    def test_import_txt(self, book_service, txt_file):
        """测试导入 TXT 文件。"""
        book_id = book_service.import_book(txt_file)
        assert book_id > 0

        book = book_service.get_book(book_id)
        assert book is not None
        assert book.title == 'test_book'
        assert book.file_format == 'txt'

    def test_import_unsupported_format(self, book_service, tmp_path):
        """测试导入不支持的格式。"""
        file_path = tmp_path / 'test.pdf'
        file_path.write_text('content', encoding='utf-8')

        with pytest.raises(ValueError, match='不支持的文件格式'):
            book_service.import_book(str(file_path))

    def test_import_nonexistent_file(self, book_service):
        """测试导入不存在的文件。"""
        with pytest.raises(FileNotFoundError):
            book_service.import_book('/nonexistent/path.epub')

    def test_import_epub(self, book_service, mini_epub):
        """测试导入 EPUB 文件。"""
        book_id = book_service.import_book(mini_epub)
        assert book_id > 0

        book = book_service.get_book(book_id)
        assert book is not None
        assert book.title == '测试电子书'
        assert book.author == '测试作者'
        assert book.file_format == 'epub'
        assert book.total_chapters == 2

    def test_remove_book(self, book_service, txt_file):
        """测试删除书籍。"""
        book_id = book_service.import_book(txt_file)
        assert book_service.get_book(book_id) is not None

        book_service.remove_book(book_id)
        assert book_service.get_book(book_id) is None

    def test_get_bookshelf(self, book_service, txt_file, mini_epub):
        """测试获取书架列表。"""
        book_service.import_book(txt_file)
        book_service.import_book(mini_epub)

        books = book_service.get_bookshelf()
        assert len(books) == 2

    def test_check_file_available_true(self, book_service, txt_file):
        """测试文件可用检查。"""
        book_id = book_service.import_book(txt_file)
        assert book_service.check_file_available(book_id) is True

    def test_check_file_available_false(self, book_service, txt_file):
        """测试文件不可用检查。"""
        book_id = book_service.import_book(txt_file)
        # 删除原始文件
        os.remove(txt_file)
        assert book_service.check_file_available(book_id) is False

    def test_update_last_read_time(self, book_service, txt_file):
        """测试更新最近阅读时间。"""
        book_id = book_service.import_book(txt_file)
        book = book_service.get_book(book_id)
        assert book.last_read_at is None

        book_service.update_last_read_time(book_id)
        book = book_service.get_book(book_id)
        assert book.last_read_at is not None

    def test_import_duplicate(self, book_service, txt_file):
        """测试重复导入同一文件（应成功创建两条记录）。"""
        id1 = book_service.import_book(txt_file)
        id2 = book_service.import_book(txt_file)
        assert id1 != id2

        books = book_service.get_bookshelf()
        assert len(books) == 2
