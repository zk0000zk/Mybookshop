"""SQLite 数据库连接管理：单例模式，自动建表。"""
from __future__ import annotations

import sqlite3
import os

from src.utils.path_utils import get_db_path


class Database:
    """SQLite 数据库连接管理（单例）。"""

    _instance: 'Database | None' = None

    def __new__(cls, db_path: str | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_db(db_path)
        return cls._instance

    def _init_db(self, db_path: str | None):
        self._db_path = db_path or get_db_path()
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        self._conn: sqlite3.Connection = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute('PRAGMA foreign_keys = ON')
        self._create_tables()

    def _create_tables(self):
        """创建数据库表（如果不存在）。"""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                title           TEXT NOT NULL,
                author          TEXT,
                file_path       TEXT NOT NULL,
                file_format     TEXT NOT NULL,
                cover_path      TEXT,
                total_chapters  INTEGER,
                file_size       INTEGER,
                imported_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_read_at    TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS reading_progress (
                book_id         INTEGER PRIMARY KEY,
                chapter_index   INTEGER NOT NULL,
                scroll_position REAL NOT NULL,
                percentage      REAL,
                updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self._conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        """执行 SQL 语句。"""
        cur = self._conn.execute(sql, params)
        self._conn.commit()
        return cur

    def fetchone(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        """查询一条记录。"""
        return self._conn.execute(sql, params).fetchone()

    def fetchall(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        """查询多条记录。"""
        return self._conn.execute(sql, params).fetchall()

    def close(self):
        """关闭数据库连接。"""
        if self._conn:
            self._conn.close()
            self._conn = None
        Database._instance = None

    @classmethod
    def reset_instance(cls):
        """重置单例（用于测试）。"""
        if cls._instance is not None:
            cls._instance.close()
        cls._instance = None
