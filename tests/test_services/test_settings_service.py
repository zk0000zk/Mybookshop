"""SettingsService 测试。"""
import pytest

from src.repository.database import Database
from src.repository.settings_repository import SettingsRepository
from src.services.settings_service import SettingsService


@pytest.fixture
def settings_service(temp_db):
    repo = SettingsRepository(temp_db)
    return SettingsService(repo)


class TestSettingsService:

    def test_get_default_settings(self, settings_service):
        """测试获取默认设置。"""
        settings = settings_service.get_settings()

        assert settings.font_size == 16
        assert settings.line_spacing == 1.8
        assert settings.theme == 'light'
        assert settings.page_mode == 'scroll'

    def test_update_font_size(self, settings_service):
        """测试更新字号。"""
        settings_service.set_font_size(20)
        assert settings_service.get('font_size') == '20'

        settings = settings_service.get_settings()
        assert settings.font_size == 20

    def test_update_line_spacing(self, settings_service):
        """测试更新行距。"""
        settings_service.set_line_spacing(2.5)
        assert settings_service.get('line_spacing') == '2.5'

    def test_update_theme(self, settings_service):
        """测试更新主题。"""
        settings_service.set_theme('dark')
        assert settings_service.get('theme') == 'dark'

    def test_update_page_mode(self, settings_service):
        """测试更新页面模式。"""
        settings_service.set_page_mode('paged')
        assert settings_service.get('page_mode') == 'paged'

    def test_invalid_theme(self, settings_service):
        """测试无效主题。"""
        with pytest.raises(ValueError):
            settings_service.set_theme('invalid')

    def test_invalid_page_mode(self, settings_service):
        """测试无效页面模式。"""
        with pytest.raises(ValueError):
            settings_service.set_page_mode('invalid')

    def test_invalid_setting_key(self, settings_service):
        """测试未知设置项。"""
        with pytest.raises(ValueError):
            settings_service.update_setting('unknown_key', 'value')

    def test_settings_persist(self, settings_service):
        """测试设置持久化。"""
        settings_service.set_font_size(24)
        settings_service.set_theme('dark')
        settings_service.set_line_spacing(2.0)

        # 重新获取
        settings = settings_service.get_settings()
        assert settings.font_size == 24
        assert settings.theme == 'dark'
        assert settings.line_spacing == 2.0
