"""阅读进度数据访问层。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.repository.database import Database


@dataclass
class ReadingProgress:
    """阅读进度数据模型。"""
    book_id: int
    chapter_index: int
    scroll_position: float
    percentage: float | None
    updated_at: str


class ProgressRepository:
    """阅读进度 Repository。"""

    def __init__(self, db: Database | None = None):
        self._db = db or Database()

    def get(self, book_id: int) -> ReadingProgress | None:
        row = self._db.fetchone(
            'SELECT * FROM reading_progress WHERE book_id = ?', (book_id,)
        )
        if not row:
            return None
        return ReadingProgress(
            book_id=row['book_id'],
            chapter_index=row['chapter_index'],
            scroll_position=row['scroll_position'],
            percentage=row['percentage'],
            updated_at=row['updated_at'],
        )

    def save(self, book_id: int, chapter_index: int,
             scroll_position: float, percentage: float | None = None) -> None:
        """保存进度（upsert）。"""
        self._db.execute(
            """INSERT INTO reading_progress (book_id, chapter_index, scroll_position, percentage, updated_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(book_id) DO UPDATE SET
                   chapter_index = excluded.chapter_index,
                   scroll_position = excluded.scroll_position,
                   percentage = excluded.percentage,
                   updated_at = excluded.updated_at""",
            (book_id, chapter_index, scroll_position, percentage, datetime.now().isoformat())
        )

    def delete(self, book_id: int) -> None:
        self._db.execute('DELETE FROM reading_progress WHERE book_id = ?', (book_id,))
