"""阅读页：渲染、翻页/滚动、工具栏、进度、自动保存。"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextBrowser, QToolBar,
    QProgressBar, QLabel, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction

from src.services.reading_service import ReadingService, ReadingState
from src.services.settings_service import SettingsService, ReadingSettings
from src.parsers.base_parser import Chapter
from src.ui.reader.toc_panel import TocPanel
from src.ui.reader.search_panel import SearchPanel
from src.ui.reader.settings_panel import SettingsPanel


class ReaderPage(QWidget):
    """阅读页。"""

    back_requested = Signal()

    # 主题 CSS 注入
    THEME_CSS = {
        'light': 'body { background: #ffffff; color: #333333; }',
        'dark': 'body { background: #1e1e1e; color: #d4d4d4; }',
    }

    def __init__(self, reading_service: ReadingService,
                 settings_service: SettingsService, parent=None):
        super().__init__(parent)
        self._reading_service = reading_service
        self._settings_service = settings_service

        self._book_id: int | None = None
        self._chapters: list[Chapter] = []
        self._current_chapter: int = 0
        self._state: ReadingState | None = None

        self._init_ui()
        self._init_timers()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏
        self._toolbar = QToolBar()
        self._toolbar.setMovable(False)
        self._toolbar.setFixedHeight(48)

        back_action = QAction('← 返回书架', self)
        back_action.triggered.connect(self._on_back)
        self._toolbar.addAction(back_action)

        self._toolbar.addSeparator()

        toc_action = QAction('📖 目录', self)
        toc_action.triggered.connect(self._toggle_toc)
        self._toolbar.addAction(toc_action)

        search_action = QAction('🔍 搜索', self)
        search_action.triggered.connect(self._toggle_search)
        self._toolbar.addAction(search_action)

        settings_action = QAction('⚙️ 设置', self)
        settings_action.triggered.connect(self._toggle_settings)
        self._toolbar.addAction(settings_action)

        self._chapter_label = QLabel('')
        self._chapter_label.setStyleSheet('margin-left: 16px; color: #666;')
        self._toolbar.addWidget(self._chapter_label)

        # 主体：QSplitter（左侧面板 + 右侧阅读区）
        self._splitter = QSplitter(Qt.Horizontal)

        # 阅读区
        self._text_browser = QTextBrowser()
        self._text_browser.setOpenExternalLinks(False)
        self._text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # 连接滚动条信号
        scroll_bar = self._text_browser.verticalScrollBar()
        scroll_bar.valueChanged.connect(self._on_scroll_value_changed)

        # 面板
        self._toc_panel = TocPanel()
        self._toc_panel.chapter_selected.connect(self._on_chapter_selected)
        self._toc_panel.setVisible(False)

        self._search_panel = SearchPanel()
        self._search_panel.search_requested.connect(self._on_search)
        self._search_panel.result_selected.connect(self._on_search_result_selected)
        self._search_panel.setVisible(False)

        self._settings_panel = SettingsPanel()
        self._settings_panel.settings_changed.connect(self._on_settings_changed)
        self._settings_panel.setVisible(False)

        self._splitter.addWidget(self._text_browser)
        self._splitter.addWidget(self._toc_panel)
        self._splitter.addWidget(self._search_panel)
        self._splitter.addWidget(self._settings_panel)
        self._splitter.setStretchFactor(0, 1)  # 阅读区占大部分空间

        # 底部进度条
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(36)
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(16, 4, 16, 4)

        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat('%p%')

        self._progress_label = QLabel('0%')

        bottom_layout.addWidget(self._progress_label)
        bottom_layout.addWidget(self._progress_bar)

        layout.addWidget(self._toolbar)
        layout.addWidget(self._splitter, 1)
        layout.addWidget(bottom_bar)

    def _init_timers(self):
        """定时自动保存进度（每 30 秒）。"""
        self._auto_save_timer = QTimer(self)
        self._auto_save_timer.timeout.connect(self._auto_save_progress)
        self._auto_save_timer.setInterval(30000)  # 30 秒

    def open_book(self, book_id: int):
        """打开书籍。"""
        try:
            self._state = self._reading_service.open_book(book_id)
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, '打开失败', f'无法打开书籍:\n{e}')
            return

        self._book_id = book_id
        self._chapters = self._state.chapters
        self._current_chapter = self._state.current_chapter

        # 更新章节标签
        if self._chapters:
            ch = self._chapters[self._current_chapter]
            self._chapter_label.setText(f'{ch.title} ({self._current_chapter + 1}/{len(self._chapters)})')

        # 加载目录面板
        if self._state.book.file_format == 'txt':
            self._toc_panel.set_no_toc()
        else:
            self._toc_panel.load_chapters(self._chapters, self._current_chapter)

        # 加载设置
        settings = self._settings_service.get_settings()
        self._settings_panel.load_settings(settings)

        # 渲染内容
        self._render_chapter(self._current_chapter)

        # 恢复滚动位置
        if self._state.scroll_position > 0:
            QTimer.singleShot(100, self._restore_scroll_position)

        # 启动自动保存定时器
        self._auto_save_timer.start()

    def _render_chapter(self, chapter_index: int):
        """渲染指定章节内容。"""
        if not (0 <= chapter_index < len(self._chapters)):
            return

        ch = self._chapters[chapter_index]
        self._current_chapter = chapter_index

        # 注入主题 CSS
        settings = self._settings_service.get_settings()
        theme_css = self.THEME_CSS.get(settings.theme, self.THEME_CSS['light'])
        font_style = f'body {{ font-size: {settings.font_size}px; line-height: {settings.line_spacing}; }}'

        full_html = f"""
        <html><head><style>
        {theme_css}
        {font_style}
        p {{ margin: 0.5em 0; text-indent: 2em; }}
        img {{ max-width: 100%; }}
        </style></head>
        <body>{ch.content}</body></html>
        """

        self._text_browser.setHtml(full_html)

        # 更新章节标签
        self._chapter_label.setText(f'{ch.title} ({chapter_index + 1}/{len(self._chapters)})')

        # 更新进度
        self._update_progress()

    def _update_progress(self):
        """更新底部进度条。"""
        if not self._chapters:
            return

        total = len(self._chapters)
        progress = (self._current_chapter + 1) / total
        percent = int(progress * 100)
        self._progress_bar.setValue(percent)
        self._progress_label.setText(f'{percent}%')

    def _restore_scroll_position(self):
        """恢复滚动位置。"""
        if self._state is None:
            return
        scroll_bar = self._text_browser.verticalScrollBar()
        max_val = scroll_bar.maximum()
        scroll_bar.setValue(int(max_val * self._state.scroll_position))

    # ---------- 事件处理 ----------
    def _on_back(self):
        """返回书架前保存进度。"""
        self._save_current_progress()
        self._auto_save_timer.stop()
        self.back_requested.emit()

    def _on_scroll_value_changed(self):
        """滚动时更新进度（但不频繁保存）。"""
        self._update_progress()

    def _on_chapter_selected(self, chapter_index: int):
        """从目录跳转章节。"""
        self._render_chapter(chapter_index)
        # 滚动到顶部
        self._text_browser.verticalScrollBar().setValue(0)
        self._save_current_progress()

    def _toggle_toc(self):
        """切换目录面板显示。"""
        self._close_other_panels(except_panel='toc')
        self._toc_panel.setVisible(not self._toc_panel.isVisible())

    def _toggle_search(self):
        """切换搜索面板显示。"""
        self._close_other_panels(except_panel='search')
        self._search_panel.setVisible(not self._search_panel.isVisible())
        if self._search_panel.isVisible():
            self._search_panel._input.setFocus()

    def _toggle_settings(self):
        """切换设置面板显示。"""
        self._close_other_panels(except_panel='settings')
        self._settings_panel.setVisible(not self._settings_panel.isVisible())

    def _close_other_panels(self, except_panel: str = ''):
        """关闭除指定面板外的所有面板。"""
        if except_panel != 'toc':
            self._toc_panel.setVisible(False)
        if except_panel != 'search':
            self._search_panel.setVisible(False)
        if except_panel != 'settings':
            self._settings_panel.setVisible(False)

    def _on_search(self, keyword: str):
        """执行搜索。"""
        if self._book_id is None:
            return
        try:
            results = self._reading_service.search_in_book(self._book_id, keyword)
            self._search_panel.show_results(results)
        except Exception as e:
            self._search_panel.show_results([])

    def _on_search_result_selected(self, chapter_index: int, snippet: str):
        """搜索结果点击跳转。"""
        self._render_chapter(chapter_index)

    def _on_settings_changed(self):
        """设置变更：即时应用。"""
        font_size = self._settings_panel.get_font_size()
        line_spacing = self._settings_panel.get_line_spacing()
        theme = self._settings_panel.get_theme()

        self._settings_service.set_font_size(font_size)
        self._settings_service.set_line_spacing(line_spacing)
        self._settings_service.set_theme(theme)

        # 重新渲染当前章节以应用新设置
        self._render_chapter(self._current_chapter)

        # 通知主窗口切换全局主题（self.window() 返回顶层 MainWindow）
        main_window = self.window()
        if hasattr(main_window, 'apply_theme'):
            main_window.apply_theme(theme)

    # ---------- 进度保存 ----------
    def _save_current_progress(self):
        """保存当前阅读进度。"""
        if self._book_id is None or not self._chapters:
            return

        scroll_bar = self._text_browser.verticalScrollBar()
        max_val = scroll_bar.maximum()
        scroll_pos = scroll_bar.value() / max_val if max_val > 0 else 0.0

        total = len(self._chapters)
        percentage = (self._current_chapter + scroll_pos) / total if total > 0 else 0.0

        self._reading_service.save_progress(
            self._book_id, self._current_chapter, scroll_pos, percentage
        )

    def _auto_save_progress(self):
        """定时自动保存。"""
        self._save_current_progress()

    def closeEvent(self, event):
        """页面关闭时保存进度。"""
        self._save_current_progress()
        self._auto_save_timer.stop()
        super().closeEvent(event)

    def keyPressEvent(self, event):
        """键盘快捷键。"""
        key = event.key()
        if key in (Qt.Key_Right, Qt.Key_PageDown):
            # 下一章
            if self._current_chapter < len(self._chapters) - 1:
                self._render_chapter(self._current_chapter + 1)
                self._text_browser.verticalScrollBar().setValue(0)
                self._save_current_progress()
        elif key in (Qt.Key_Left, Qt.Key_PageUp):
            # 上一章
            if self._current_chapter > 0:
                self._render_chapter(self._current_chapter - 1)
                self._text_browser.verticalScrollBar().setValue(0)
                self._save_current_progress()
        elif key == Qt.Key_Escape:
            self._on_back()
        else:
            super().keyPressEvent(event)
