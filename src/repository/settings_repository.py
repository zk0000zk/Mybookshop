"""设置数据访问层（KV 结构）。"""
from __future__ import annotations

from src.repository.database import Database


# 默认设置值
DEFAULT_SETTINGS = {
    'font_size': '16',
    'line_spacing': '1.8',
    'theme': 'light',
    'page_mode': 'scroll',
}


class SettingsRepository:
    """设置 Repository，KV 存储。"""

    def __init__(self, db: Database | None = None):
        self._db = db or Database()
        self._ensure_defaults()

    def _ensure_defaults(self):
        """确保默认设置存在。"""
        for key, value in DEFAULT_SETTINGS.items():
            existing = self._db.fetchone('SELECT key FROM settings WHERE key = ?', (key,))
            if not existing:
                self._db.execute(
                    'INSERT INTO settings (key, value) VALUES (?, ?)', (key, value)
                )

    def get(self, key: str, default: str = '') -> str:
        row = self._db.fetchone('SELECT value FROM settings WHERE key = ?', (key,))
        if row:
            return row['value']
        return default

    def set(self, key: str, value: str) -> None:
        self._db.execute(
            """INSERT INTO settings (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            (key, value)
        )

    def get_all(self) -> dict[str, str]:
        rows = self._db.fetchall('SELECT key, value FROM settings')
        result = {}
        for row in rows:
            result[row['key']] = row['value']
        # 补充默认值
        for key, value in DEFAULT_SETTINGS.items():
            if key not in result:
                result[key] = value
        return result
