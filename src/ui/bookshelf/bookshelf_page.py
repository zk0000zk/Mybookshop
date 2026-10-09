"""书架页：导入、列表、删除。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QScrollArea, QGridLayout, QFrame, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog

from src.services.book_service import BookService
from src.services.reading_service import ReadingService
from src.ui.bookshelf.book_card import BookCard
from src.ui.widgets.empty_state import EmptyState


class BookshelfPage(QWidget):
    """书架页。"""

    open_book_requested = Signal(int)

    def __init__(self, book_service: BookService, reading_service: ReadingService, parent=None):
        super().__init__(parent)
        self._book_service = book_service
        self._reading_service = reading_service

        self._init_ui()
        self.refresh()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部工具栏
        toolbar = QFrame()
        toolbar.setFixedHeight(56)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(16, 8, 16, 8)

        title_label = QLabel('📚 我的书架')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText('搜索书名...')
        self._search_input.setFixedWidth(200)
        self._search_input.textChanged.connect(self._on_search_changed)

        import_btn = QPushButton('导入书籍')
        import_btn.setObjectName('primaryButton')
        import_btn.clicked.connect(self._on_import_clicked)

        toolbar_layout.addWidget(title_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self._search_input)
        toolbar_layout.addWidget(import_btn)

        # 内容区域（滚动）
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setObjectName('bookshelfScroll')

        self._content_container = QFrame()
        self._content_container.setObjectName('bookshelfContainer')
        self._grid_layout = QGridLayout(self._content_container)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setContentsMargins(20, 20, 20, 20)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        self._scroll_area.setWidget(self._content_container)

        # 空状态
        self._empty_state = EmptyState('还没有书籍，点击「导入书籍」添加本地 EPUB 或 TXT 文件')

        layout.addWidget(toolbar)
        layout.addWidget(self._scroll_area)
        layout.addWidget(self._empty_state)

    def refresh(self):
        """刷新书架列表。"""
        # 清除现有卡片
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        books = self._book_service.get_bookshelf()

        # 过滤
        search_text = self._search_input.text().strip().lower()
        if search_text:
            books = [b for b in books if search_text in (b.title or '').lower()
                     or search_text in (b.author or '').lower()]

        if not books:
            self._empty_state.setVisible(True)
            self._scroll_area.setVisible(False)
            return

        self._empty_state.setVisible(False)
        self._scroll_area.setVisible(True)

        # 网格布局，每行 5 本
        columns = 5
        for i, book in enumerate(books):
            progress = 0.0
            prog = self._reading_service.get_progress(book.id)
            if prog and book.total_chapters > 0:
                progress = (prog.chapter_index + prog.scroll_position) / book.total_chapters
                progress = min(progress, 1.0)

            card = BookCard(book, progress)
            card.open_requested.connect(self._on_open_book)
            card.delete_requested.connect(self._on_delete_book)

            row = i // columns
            col = i % columns
            self._grid_layout.addWidget(card, row, col)

    def _on_import_clicked(self):
        """打开文件选择对话框导入书籍。"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, '选择电子书文件', '',
            '电子书文件 (*.epub *.txt);;EPUB 文件 (*.epub);;文本文件 (*.txt);;所有文件 (*.*)'
        )
        if not file_paths:
            return

        success_count = 0
        errors = []
        for fp in file_paths:
            try:
                self._book_service.import_book(fp)
                success_count += 1
            except FileNotFoundError:
                errors.append(f'{fp}: 文件不存在')
            except ValueError as e:
                errors.append(f'{fp}: {e}')
            except Exception as e:
                errors.append(f'{fp}: {e}')

        if success_count:
            self.refresh()

        if errors:
            QMessageBox.warning(
                self, '部分导入失败',
                f'成功导入 {success_count} 本，{len(errors)} 本失败:\n\n' + '\n'.join(errors)
            )

    def _on_open_book(self, book_id: int):
        """打开书籍。"""
        if not self._book_service.check_file_available(book_id):
            reply = QMessageBox.question(
                self, '文件不可用',
                '该书籍的原始文件可能已被移动或删除。\n是否从书架移除该记录？',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._book_service.remove_book(book_id)
                self.refresh()
            return

        self.open_book_requested.emit(book_id)

    def _on_delete_book(self, book_id: int):
        """删除书籍记录。"""
        book = self._book_service.get_book(book_id)
        if not book:
            return

        reply = QMessageBox.question(
            self, '确认移除',
            f'确定从书架移除《{book.title}》吗？\n（仅删除书架记录，不删除原始文件）',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._book_service.remove_book(book_id)
            self.refresh()

    def _on_search_changed(self):
        self.refresh()
