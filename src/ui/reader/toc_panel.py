"""目录面板：EPUB 章节树，点击跳转。"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PySide6.QtCore import Qt, Signal

from src.parsers.base_parser import Chapter


class TocPanel(QWidget):
    """目录面板。"""

    chapter_selected = Signal(int)  # chapter_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        label = QLabel('目录')
        label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(label)
        layout.addWidget(self._tree)

    def load_chapters(self, chapters: list[Chapter], current_index: int = 0):
        """加载章节列表。"""
        self._tree.clear()
        for ch in chapters:
            item = QTreeWidgetItem([f'{ch.index + 1}. {ch.title}'])
            item.setData(0, Qt.UserRole, ch.index)
            if ch.index == current_index:
                item.setSelected(True)
            self._tree.addTopLevelItem(item)

        # 滚动到当前章节
        if current_index < self._tree.topLevelItemCount():
            self._tree.setCurrentItem(self._tree.topLevelItem(current_index))

    def _on_item_clicked(self, item: QTreeWidgetItem):
        chapter_index = item.data(0, Qt.UserRole)
        if chapter_index is not None:
            self.chapter_selected.emit(chapter_index)

    def set_no_toc(self):
        """TXT 无目录时显示提示。"""
        self._tree.clear()
        item = QTreeWidgetItem(['（TXT 文件无目录）'])
        item.setFlags(Qt.NoItemFlags)
        self._tree.addTopLevelItem(item)
