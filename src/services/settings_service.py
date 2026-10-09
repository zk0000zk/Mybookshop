"""设置服务：读取、更新阅读设置。"""
from __future__ import annotations

from dataclasses import dataclass

from src.repository.settings_repository import SettingsRepository, DEFAULT_SETTINGS


@dataclass
class ReadingSettings:
    """结构化阅读设置。"""
    font_size: int = int(DEFAULT_SETTINGS['font_size'])
    line_spacing: float = float(DEFAULT_SETTINGS['line_spacing'])
    theme: str = DEFAULT_SETTINGS['theme']
    page_mode: str = DEFAULT_SETTINGS['page_mode']


class SettingsService:
    """设置业务逻辑层。"""

    def __init__(self, settings_repo: SettingsRepository | None = None):
        self._repo = settings_repo or SettingsRepository()

    def get_settings(self) -> ReadingSettings:
        """读取全部设置，返回结构化对象。"""
        all_settings = self._repo.get_all()
        return ReadingSettings(
            font_size=int(all_settings.get('font_size', DEFAULT_SETTINGS['font_size'])),
            line_spacing=float(all_settings.get('line_spacing', DEFAULT_SETTINGS['line_spacing'])),
            theme=all_settings.get('theme', DEFAULT_SETTINGS['theme']),
            page_mode=all_settings.get('page_mode', DEFAULT_SETTINGS['page_mode']),
        )

    def update_setting(self, key: str, value: str) -> None:
        """更新单个设置。"""
        if key not in DEFAULT_SETTINGS:
            raise ValueError(f'未知设置项: {key}')
        self._repo.set(key, value)

    def get(self, key: str) -> str:
        return self._repo.get(key, DEFAULT_SETTINGS.get(key, ''))

    def set_font_size(self, size: int) -> None:
        self.update_setting('font_size', str(size))

    def set_line_spacing(self, spacing: float) -> None:
        self.update_setting('line_spacing', str(spacing))

    def set_theme(self, theme: str) -> None:
        if theme not in ('light', 'dark'):
            raise ValueError(f'无效主题: {theme}')
        self.update_setting('theme', theme)

    def set_page_mode(self, mode: str) -> None:
        if mode not in ('scroll', 'paged'):
            raise ValueError(f'无效页面模式: {mode}')
        self.update_setting('page_mode', mode)
