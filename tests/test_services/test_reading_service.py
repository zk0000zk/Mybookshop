"""ReadingService 测试。"""
import pytest

from src.repository.database import Database
from src.repository.book_repository import BookRepository
from src.repository.progress_repository import ProgressRepository
from src.services.book_service import BookService
from src.services.reading_service import ReadingService


@pytest.fixture
def reading_service(temp_db):
    book_repo = BookRepository(temp_db)
    progress_repo = ProgressRepository(temp_db)
    book_service = BookService(book_repo)
    return book_service, ReadingService(book_repo, progress_repo)


class TestReadingService:

    def test_open_book_txt(self, reading_service, txt_file):
        """测试打开 TXT 书籍。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(txt_file)

        state = rs.open_book(book_id)
        assert state.book.id == book_id
        assert len(state.chapters) == 1
        assert state.current_chapter == 0
        assert state.scroll_position == 0.0

    def test_open_book_epub(self, reading_service, mini_epub):
        """测试打开 EPUB 书籍。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        state = rs.open_book(book_id)
        assert len(state.chapters) == 2
        assert state.current_chapter == 0

    def test_open_nonexistent_book(self, reading_service):
        """测试打开不存在的书籍。"""
        _, rs = reading_service
        with pytest.raises(ValueError, match='书籍不存在'):
            rs.open_book(999)

    def test_save_and_restore_progress(self, reading_service, mini_epub):
        """测试保存并恢复进度。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        # 打开书
        state = rs.open_book(book_id)
        assert state.current_chapter == 0

        # 保存进度到第 1 章，滚动位置 0.5
        rs.save_progress(book_id, chapter_index=1, scroll_position=0.5, percentage=0.75)

        # 重新打开，应该恢复到第 1 章
        state = rs.open_book(book_id)
        assert state.current_chapter == 1
        assert state.scroll_position == 0.5

    def test_save_progress_updates_last_read(self, reading_service, mini_epub):
        """测试保存进度时更新最近阅读时间。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        book = book_service.get_book(book_id)
        assert book.last_read_at is None

        rs.save_progress(book_id, chapter_index=0, scroll_position=0.0)

        book = book_service.get_book(book_id)
        assert book.last_read_at is not None

    def test_get_progress_nonexistent(self, reading_service, txt_file):
        """测试获取不存在的进度。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(txt_file)

        progress = rs.get_progress(book_id)
        assert progress is None

    def test_search_in_book_txt(self, reading_service, txt_file):
        """测试 TXT 搜索。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(txt_file)

        results = rs.search_in_book(book_id, 'mykeyword')
        assert len(results) == 2

    def test_search_in_book_epub(self, reading_service, mini_epub):
        """测试 EPUB 搜索。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        results = rs.search_in_book(book_id, 'mykeyword')
        assert len(results) == 2

    def test_search_no_match(self, reading_service, txt_file):
        """测试搜索无匹配。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(txt_file)

        results = rs.search_in_book(book_id, '不存在xyz')
        assert len(results) == 0

    def test_get_chapters_txt(self, reading_service, txt_file):
        """测试获取 TXT 章节。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(txt_file)

        chapters = rs.get_chapters(book_id)
        assert len(chapters) == 1
        assert chapters[0].title == '全文'

    def test_get_chapters_epub(self, reading_service, mini_epub):
        """测试获取 EPUB 章节。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        chapters = rs.get_chapters(book_id)
        assert len(chapters) == 2

    def test_open_book_progress_out_of_range(self, reading_service, mini_epub):
        """测试进度越界时自动重置。"""
        book_service, rs = reading_service
        book_id = book_service.import_book(mini_epub)

        # 保存越界的进度
        rs.save_progress(book_id, chapter_index=999, scroll_position=0.5)

        # 打开时应该重置到 0
        state = rs.open_book(book_id)
        assert state.current_chapter == 0
        assert state.scroll_position == 0.0
