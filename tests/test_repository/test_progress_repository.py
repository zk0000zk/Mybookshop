"""ProgressRepository 测试。"""
import pytest

from src.repository.database import Database
from src.repository.book_repository import BookRepository
from src.repository.progress_repository import ProgressRepository


@pytest.fixture
def setup(temp_db):
    book_repo = BookRepository(temp_db)
    progress_repo = ProgressRepository(temp_db)
    book_id = book_repo.add('书', None, '/path/test.txt', 'txt', None, 1, 100)
    return book_repo, progress_repo, book_id


class TestProgressRepository:

    def test_save_and_get(self, setup):
        """测试保存并获取进度。"""
        _, progress_repo, book_id = setup

        progress_repo.save(book_id, chapter_index=2, scroll_position=0.5)

        progress = progress_repo.get(book_id)
        assert progress is not None
        assert progress.book_id == book_id
        assert progress.chapter_index == 2
        assert progress.scroll_position == 0.5

    def test_get_nonexistent(self, setup):
        """测试获取不存在的进度。"""
        _, progress_repo, _ = setup
        progress = progress_repo.get(999)
        assert progress is None

    def test_update_progress(self, setup):
        """测试更新已有进度（upsert）。"""
        _, progress_repo, book_id = setup

        progress_repo.save(book_id, chapter_index=0, scroll_position=0.1)
        progress_repo.save(book_id, chapter_index=3, scroll_position=0.8)

        progress = progress_repo.get(book_id)
        assert progress.chapter_index == 3
        assert progress.scroll_position == 0.8

    def test_delete_progress(self, setup):
        """测试删除进度。"""
        _, progress_repo, book_id = setup

        progress_repo.save(book_id, chapter_index=1, scroll_position=0.3)
        progress_repo.delete(book_id)

        assert progress_repo.get(book_id) is None

    def test_cascade_delete(self, setup):
        """测试级联删除：删除书籍时进度也应删除。"""
        book_repo, progress_repo, book_id = setup

        progress_repo.save(book_id, chapter_index=1, scroll_position=0.3)
        assert progress_repo.get(book_id) is not None

        book_repo.delete(book_id)
        assert progress_repo.get(book_id) is None

    def test_save_with_percentage(self, setup):
        """测试保存带百分比的进度。"""
        _, progress_repo, book_id = setup

        progress_repo.save(book_id, chapter_index=2, scroll_position=0.5, percentage=0.25)

        progress = progress_repo.get(book_id)
        assert progress.percentage == 0.25
