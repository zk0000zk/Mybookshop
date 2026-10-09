"""主窗口：页面切换容器。"""
from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QStackedWidget
from PySide6.QtCore import Qt

from src.services.book_service import BookService
from src.services.reading_service import ReadingService
from src.services.settings_service import SettingsService
from src.ui.bookshelf.bookshelf_page import BookshelfPage
from src.ui.reader.reader_page import ReaderPage
from src.utils.path_utils import get_resource_path


class MainWindow(QMainWindow):
    """主窗口：管理书架页和阅读页的切换。"""

    BOOKSHELF_PAGE = 0
    READER_PAGE = 1

    def __init__(self):
        super().__init__()
        self.setWindowTitle('电子书阅读器')
        self.setMinimumSize(900, 640)
        self.resize(1200, 800)

        # 初始化服务
        self._book_service = BookService()
        self._reading_service = ReadingService()
        self._settings_service = SettingsService()

        # 初始化页面
        self._stack = QStackedWidget()
        self._bookshelf_page = BookshelfPage(self._book_service, self._reading_service)
        self._reader_page = ReaderPage(self._reading_service, self._settings_service)

        self._stack.addWidget(self._bookshelf_page)  # index 0
        self._stack.addWidget(self._reader_page)     # index 1

        self.setCentralWidget(self._stack)

        # 连接信号
        self._bookshelf_page.open_book_requested.connect(self._open_book)
        self._reader_page.back_requested.connect(self._back_to_bookshelf)

        # 应用主题
        self._apply_theme_from_settings()

    def _open_book(self, book_id: int):
        """切换到阅读页并打开书籍。"""
        self._stack.setCurrentIndex(self.READER_PAGE)
        self._reader_page.open_book(book_id)

    def _back_to_bookshelf(self):
        """返回书架页。"""
        self._bookshelf_page.refresh()
        self._stack.setCurrentIndex(self.BOOKSHELF_PAGE)

    def _apply_theme_from_settings(self):
        """从设置读取主题并应用。"""
        settings = self._settings_service.get_settings()
        self.apply_theme(settings.theme)

    def apply_theme(self, theme: str):
        """应用全局主题 QSS。"""
        from PySide6.QtWidgets import QApplication
        qss_file = get_resource_path(f'resources/{theme}.qss')
        try:
            with open(qss_file, 'r', encoding='utf-8') as f:
                qss = f.read()
            QApplication.instance().setStyleSheet(qss)
        except FileNotFoundError:
            pass

        # 持久化主题设置
        self._settings_service.set_theme(theme)

    def closeEvent(self, event):
        """窗口关闭时保存进度。"""
        if self._stack.currentIndex() == self.READER_PAGE:
            self._reader_page._save_current_progress()
        super().closeEvent(event)
