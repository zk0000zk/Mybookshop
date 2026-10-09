"""书籍卡片组件。"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QProgressBar, QMenu
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QPixmap

from src.repository.book_repository import Book
from src.utils.path_utils import format_datetime


class BookCard(QFrame):
    """单本书籍的卡片组件，展示封面、书名、作者、时间、进度。"""

    open_requested = Signal(int)    # book_id
    delete_requested = Signal(int)  # book_id

    def __init__(self, book: Book, progress_percent: float = 0.0, parent=None):
        super().__init__(parent)
        self._book = book
        self._progress = progress_percent
        self.setObjectName('bookCard')
        self.setFixedSize(160, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # 封面区
        cover_label = QLabel()
        cover_label.setFixedSize(140, 180)
        cover_label.setAlignment(Qt.AlignCenter)
        cover_label.setStyleSheet('background-color: #e0e0e0; border-radius: 4px;')

        if book.cover_path:
            pixmap = QPixmap(book.cover_path)
            if not pixmap.isNull():
                cover_label.setPixmap(
                    pixmap.scaled(140, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )
        else:
            # 无封面，显示书名首字
            cover_label.setText(book.title[:1] if book.title else '?')
            font = cover_label.font()
            font.setPointSize(36)
            font.setBold(True)
            cover_label.setFont(font)
            cover_label.setStyleSheet(
                'background-color: #1976D2; color: white; border-radius: 4px; font-size: 36px; font-weight: bold;'
            )

        # 书名
        title_label = QLabel(book.title)
        title_label.setObjectName('bookTitle')
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(36)

        # 作者 / 时间
        meta_parts = []
        if book.author:
            meta_parts.append(book.author)
        meta_parts.append(format_datetime(book.last_read_at))
        meta_label = QLabel(' · '.join(meta_parts))
        meta_label.setObjectName('bookMeta')

        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(int(progress_percent * 100))
        progress_bar.setTextVisible(True)
        progress_bar.setFormat(f'{int(progress_percent * 100)}%')
        progress_bar.setFixedHeight(12)

        layout.addWidget(cover_label, alignment=Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(meta_label)
        layout.addWidget(progress_bar)

        # 右键菜单
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def mouseDoubleClickEvent(self, event):
        """双击打开书籍。"""
        self.open_requested.emit(self._book.id)
        super().mouseDoubleClickEvent(event)

    def _show_context_menu(self, pos):
        menu = QMenu(self)

        open_action = QAction('打开', self)
        open_action.triggered.connect(lambda: self.open_requested.emit(self._book.id))

        delete_action = QAction('从书架移除', self)
        delete_action.triggered.connect(lambda: self.delete_requested.emit(self._book.id))

        menu.addAction(open_action)
        menu.addAction(delete_action)
        menu.exec(self.mapToGlobal(pos))
