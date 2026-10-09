"""SettingsRepository 测试。"""
import pytest

from src.repository.database import Database
from src.repository.settings_repository import SettingsRepository, DEFAULT_SETTINGS


@pytest.fixture
def settings_repo(temp_db):
    return SettingsRepository(temp_db)


class TestSettingsRepository:

    def test_default_settings_exist(self, settings_repo):
        """测试默认设置已初始化。"""
        all_settings = settings_repo.get_all()
        assert 'font_size' in all_settings
        assert 'line_spacing' in all_settings
        assert 'theme' in all_settings
        assert 'page_mode' in all_settings

        assert all_settings['font_size'] == '16'
        assert all_settings['line_spacing'] == '1.8'
        assert all_settings['theme'] == 'light'
        assert all_settings['page_mode'] == 'scroll'

    def test_get(self, settings_repo):
        """测试读取设置。"""
        assert settings_repo.get('font_size') == '16'
        assert settings_repo.get('theme') == 'light'

    def test_get_with_default(self, settings_repo):
        """测试读取不存在的键，返回默认值。"""
        assert settings_repo.get('nonexistent_key', 'fallback') == 'fallback'

    def test_set(self, settings_repo):
        """测试更新设置。"""
        settings_repo.set('font_size', '20')
        assert settings_repo.get('font_size') == '20'

    def test_set_overwrite(self, settings_repo):
        """测试覆盖已有设置。"""
        settings_repo.set('theme', 'dark')
        assert settings_repo.get('theme') == 'dark'

        settings_repo.set('theme', 'light')
        assert settings_repo.get('theme') == 'light'

    def test_get_all(self, settings_repo):
        """测试获取全部设置。"""
        settings_repo.set('font_size', '18')
        settings_repo.set('theme', 'dark')

        all_settings = settings_repo.get_all()
        assert all_settings['font_size'] == '18'
        assert all_settings['theme'] == 'dark'
        assert all_settings['line_spacing'] == '1.8'  # 未修改的保持默认
