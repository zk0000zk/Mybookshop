"""阅读服务：打开书籍、进度保存/恢复、书内搜索。"""
from __future__ import annotations

from dataclasses import dataclass

from src.parsers.epub_parser import EpubParser
from src.parsers.txt_parser import TxtParser
from src.parsers.base_parser import Chapter
from src.repository.book_repository import BookRepository, Book
from src.repository.progress_repository import ProgressRepository, ReadingProgress

PARSERS = {
    'epub': EpubParser(),
    'txt': TxtParser(),
}


@dataclass
class ReadingState:
    """打开书籍后的初始阅读状态。"""
    book: Book
    chapters: list[Chapter]
    current_chapter: int
    scroll_position: float


class ReadingService:
    """阅读业务逻辑层。"""

    def __init__(self, book_repo: BookRepository | None = None,
                 progress_repo: ProgressRepository | None = None):
        self._book_repo = book_repo or BookRepository()
        self._progress_repo = progress_repo or ProgressRepository()

    def open_book(self, book_id: int) -> ReadingState:
        """
        打开书籍：加载书籍信息 → 查进度 → 获取章节内容 → 返回初始状态。
        """
        book = self._book_repo.get_by_id(book_id)
        if book is None:
            raise ValueError(f'书籍不存在: book_id={book_id}')

        parser = PARSERS.get(book.file_format)
        if parser is None:
            raise ValueError(f'不支持的格式: {book.file_format}')

        chapters = parser.get_chapters(book.file_path)
        if not chapters:
            raise ValueError('无法获取章节内容，文件可能已损坏')

        # 查进度
        progress = self._progress_repo.get(book_id)
        current_chapter = progress.chapter_index if progress else 0
        scroll_position = progress.scroll_position if progress else 0.0

        # 防止越界
        if current_chapter >= len(chapters):
            current_chapter = 0
            scroll_position = 0.0

        # 更新最近阅读时间
        self._book_repo.update_last_read_time(book_id)

        return ReadingState(
            book=book,
            chapters=chapters,
            current_chapter=current_chapter,
            scroll_position=scroll_position,
        )

    def save_progress(self, book_id: int, chapter_index: int,
                      scroll_position: float, percentage: float | None = None) -> None:
        """保存阅读进度并更新最近阅读时间。"""
        self._progress_repo.save(book_id, chapter_index, scroll_position, percentage)
        self._book_repo.update_last_read_time(book_id)

    def get_progress(self, book_id: int) -> ReadingProgress | None:
        return self._progress_repo.get(book_id)

    def search_in_book(self, book_id: int, keyword: str) -> list[dict]:
        """在书中搜索关键词，返回匹配结果列表。"""
        book = self._book_repo.get_by_id(book_id)
        if book is None:
            raise ValueError(f'书籍不存在: book_id={book_id}')

        parser = PARSERS.get(book.file_format)
        if parser is None:
            raise ValueError(f'不支持的格式: {book.file_format}')

        if hasattr(parser, 'search_in_chapters'):
            return parser.search_in_chapters(book.file_path, keyword)
        return []

    def get_chapters(self, book_id: int) -> list[Chapter]:
        """获取书籍所有章节。"""
        book = self._book_repo.get_by_id(book_id)
        if book is None:
            raise ValueError(f'书籍不存在: book_id={book_id}')

        parser = PARSERS.get(book.file_format)
        if parser is None:
            raise ValueError(f'不支持的格式: {book.file_format}')

        return parser.get_chapters(book.file_path)
