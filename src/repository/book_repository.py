"""书籍数据访问层。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os

from src.repository.database import Database


@dataclass
class Book:
    """书籍数据模型（对应 books 表）。"""
    id: int
    title: str
    author: str | None
    file_path: str
    file_format: str
    cover_path: str | None
    total_chapters: int
    file_size: int
    imported_at: str
    last_read_at: str | None


class BookRepository:
    """书籍 Repository。"""

    def __init__(self, db: Database | None = None):
        self._db = db or Database()

    def add(self, title: str, author: str | None, file_path: str,
            file_format: str, cover_path: str | None,
            total_chapters: int, file_size: int) -> int:
        """添加一本书到书架，返回 book_id。"""
        cur = self._db.execute(
            """INSERT INTO books (title, author, file_path, file_format, cover_path,
                                   total_chapters, file_size, imported_at, last_read_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (title, author, file_path, file_format, cover_path,
             total_chapters, file_size, datetime.now().isoformat(), None)
        )
        return cur.lastrowid

    def get_by_id(self, book_id: int) -> Book | None:
        row = self._db.fetchone('SELECT * FROM books WHERE id = ?', (book_id,))
        return self._row_to_book(row) if row else None

    def list_all(self) -> list[Book]:
        rows = self._db.fetchall(
            'SELECT * FROM books ORDER BY last_read_at DESC NULLS LAST, imported_at DESC'
        )
        return [self._row_to_book(r) for r in rows]

    def delete(self, book_id: int) -> None:
        # 外键级联删除会自动删除 reading_progress
        self._db.execute('DELETE FROM books WHERE id = ?', (book_id,))

    def update_last_read_time(self, book_id: int) -> None:
        self._db.execute(
            'UPDATE books SET last_read_at = ? WHERE id = ?',
            (datetime.now().isoformat(), book_id)
        )

    def check_file_exists(self, book_id: int) -> bool:
        row = self._db.fetchone('SELECT file_path FROM books WHERE id = ?', (book_id,))
        if not row:
            return False
        return os.path.exists(row['file_path'])

    @staticmethod
    def _row_to_book(row) -> Book:
        return Book(
            id=row['id'],
            title=row['title'],
            author=row['author'],
            file_path=row['file_path'],
            file_format=row['file_format'],
            cover_path=row['cover_path'],
            total_chapters=row['total_chapters'] or 0,
            file_size=row['file_size'] or 0,
            imported_at=row['imported_at'],
            last_read_at=row['last_read_at'],
        )
