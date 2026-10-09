"""空状态提示组件。"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class EmptyState(QWidget):
    """空状态提示组件，居中显示图标和文字。"""

    def __init__(self, text: str = '导入本地书籍', parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel('📚')
        icon_label.setAlignment(Qt.AlignCenter)
        font = icon_label.font()
        font.setPointSize(64)
        icon_label.setFont(font)

        hint_label = QLabel(text)
        hint_label.setObjectName('emptyHint')
        hint_label.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(icon_label)
        layout.addWidget(hint_label)
        layout.addStretch()
