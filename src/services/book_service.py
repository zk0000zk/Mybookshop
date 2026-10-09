"""书籍服务：导入、删除、列表、文件可用性检查。"""
from __future__ import annotations

import os

from src.parsers.epub_parser import EpubParser
from src.parsers.txt_parser import TxtParser
from src.repository.book_repository import BookRepository, Book


# 格式 → Parser 映射
PARSERS = {
    'epub': EpubParser(),
    'txt': TxtParser(),
}

SUPPORTED_FORMATS = ('.epub', '.txt')


class BookService:
    """书籍业务逻辑层。"""

    def __init__(self, book_repo: BookRepository | None = None):
        self._book_repo = book_repo or BookRepository()

    def import_book(self, file_path: str) -> int:
        """
        导入书籍：判断格式 → 解析元数据 → 存入数据库。
        返回 book_id。
        如果格式不支持或解析失败，抛出 ValueError。
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'文件不存在: {file_path}')

        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if ext not in PARSERS:
            raise ValueError(
                f'不支持的文件格式: .{ext}，仅支持 {"、".join(SUPPORTED_FORMATS)}'
            )

        parser = PARSERS[ext]
        try:
            metadata = parser.parse_metadata(file_path)
        except Exception as e:
            raise ValueError(f'解析文件失败: {e}')

        book_id = self._book_repo.add(
            title=metadata.title,
            author=metadata.author,
            file_path=metadata.file_path,
            file_format=metadata.file_format,
            cover_path=metadata.cover_path,
            total_chapters=metadata.total_chapters,
            file_size=metadata.file_size,
        )
        return book_id

    def remove_book(self, book_id: int) -> None:
        """删除书架记录（不删原文件），同时级联删除进度。"""
        self._book_repo.delete(book_id)

    def get_bookshelf(self) -> list[Book]:
        """获取书架列表，按最近阅读时间排序。"""
        return self._book_repo.list_all()

    def get_book(self, book_id: int) -> Book | None:
        return self._book_repo.get_by_id(book_id)

    def check_file_available(self, book_id: int) -> bool:
        """检查原始文件是否还存在。"""
        return self._book_repo.check_file_exists(book_id)

    def update_last_read_time(self, book_id: int) -> None:
        self._book_repo.update_last_read_time(book_id)
