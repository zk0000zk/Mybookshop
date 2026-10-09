"""BookshelfPage UI 测试。
需要 PySide6 和 pytest-qt。
"""
import pytest

pytest.importorskip("PySide6")
pytest.importorskip("pytestqt")

from src.repository.database import Database
from src.repository.book_repository import BookRepository
from src.repository.progress_repository import ProgressRepository
from src.services.book_service import BookService
from src.services.reading_service import ReadingService
from src.ui.bookshelf.bookshelf_page import BookshelfPage
from src.ui.widgets.empty_state import EmptyState


@pytest.fixture
def bookshelf_page(temp_db, qtbot):
    """创建书架页实例。"""
    book_repo = BookRepository(temp_db)
    progress_repo = ProgressRepository(temp_db)
    book_service = BookService(book_repo)
    reading_service = ReadingService(book_repo, progress_repo)

    page = BookshelfPage(book_service, reading_service)
    qtbot.addWidget(page)
    return page, book_service


class TestBookshelfPage:

    def test_empty_state_visible(self, bookshelf_page):
        """空书架应显示空状态提示。"""
        page, _ = bookshelf_page
        assert page._empty_state.isVisible()
        assert not page._scroll_area.isVisible()

    def test_import_book_shows_card(self, bookshelf_page, txt_file):
        """导入书籍后应显示卡片，隐藏空状态。"""
        page, book_service = bookshelf_page
        book_service.import_book(txt_file)
        page.refresh()

        assert not page._empty_state.isVisible()
        assert page._scroll_area.isVisible()
        assert page._grid_layout.count() == 1

    def test_import_multiple_books(self, bookshelf_page, txt_file, mini_epub):
        """导入多本书后应显示多个卡片。"""
        page, book_service = bookshelf_page
        book_service.import_book(txt_file)
        book_service.import_book(mini_epub)
        page.refresh()

        assert page._grid_layout.count() == 2

    def test_search_filter(self, bookshelf_page, txt_file, mini_epub):
        """搜索应过滤书籍列表。"""
        page, book_service = bookshelf_page
        book_service.import_book(txt_file)
        book_service.import_book(mini_epub)
        page.refresh()
        assert page._grid_layout.count() == 2

        # 搜索 "测试"
        page._search_input.setText("测试电子书")
        assert page._grid_layout.count() == 1

        # 清除搜索
        page._search_input.setText("")
        assert page._grid_layout.count() == 2

    def test_delete_book(self, bookshelf_page, txt_file):
        """删除书籍后应刷新列表。"""
        page, book_service = bookshelf_page
        book_id = book_service.import_book(txt_file)
        page.refresh()
        assert page._grid_layout.count() == 1

        book_service.remove_book(book_id)
        page.refresh()
        assert page._grid_layout.count() == 0
        assert page._empty_state.isVisible()

    def test_empty_state_component(self, temp_db, qtbot):
        """空状态组件基本测试。"""
        empty = EmptyState("测试提示")
        qtbot.addWidget(empty)
        assert empty is not None
