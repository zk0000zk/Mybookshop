"""搜索面板：输入关键词，显示匹配结果，点击跳转。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QLabel
)
from PySide6.QtCore import Qt, Signal

from src.utils.text_utils import highlight_keyword


class SearchPanel(QWidget):
    """搜索面板。"""

    search_requested = Signal(str)               # keyword
    result_selected = Signal(int, str)           # chapter_index, snippet

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        label = QLabel('搜索')
        label.setStyleSheet('font-size: 16px; font-weight: bold;')

        self._input = QLineEdit()
        self._input.setPlaceholderText('输入关键词...')
        self._input.returnPressed.connect(self._on_search)

        self._result_list = QListWidget()
        self._result_list.itemClicked.connect(self._on_result_clicked)

        self._status_label = QLabel('')
        self._status_label.setStyleSheet('font-size: 12px; color: #888;')

        layout.addWidget(label)
        layout.addWidget(self._input)
        layout.addWidget(self._status_label)
        layout.addWidget(self._result_list)

    def _on_search(self):
        keyword = self._input.text().strip()
        if keyword:
            self.search_requested.emit(keyword)

    def show_results(self, results: list[dict]):
        """显示搜索结果。"""
        self._result_list.clear()
        if not results:
            self._status_label.setText('未找到匹配结果')
            return

        self._status_label.setText(f'找到 {len(results)} 个结果')

        for r in results:
            highlighted = highlight_keyword(r['snippet'], r['keyword'])
            display_text = f"[{r['chapter_title']}] ...{highlighted}..."
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, (r['chapter_index'], r['snippet']))
            self._result_list.addItem(item)

    def _on_result_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if data:
            chapter_index, snippet = data
            self.result_selected.emit(chapter_index, snippet)
