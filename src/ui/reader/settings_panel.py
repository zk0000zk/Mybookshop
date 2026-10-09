"""阅读设置面板：字号、行距、主题切换。"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal

from src.services.settings_service import ReadingSettings


class SettingsPanel(QWidget):
    """阅读设置面板。"""

    settings_changed = Signal()  # 设置变更信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        title = QLabel('阅读设置')
        title.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title)

        # 字号
        font_layout = QHBoxLayout()
        font_label = QLabel(f'字号')
        font_label.setFixedWidth(60)
        self._font_value_label = QLabel('16 px')
        self._font_value_label.setFixedWidth(50)

        self._font_slider = QSlider(Qt.Horizontal)
        self._font_slider.setRange(12, 32)
        self._font_slider.setValue(16)
        self._font_slider.valueChanged.connect(self._on_font_changed)

        font_layout.addWidget(font_label)
        font_layout.addWidget(self._font_slider)
        font_layout.addWidget(self._font_value_label)
        layout.addLayout(font_layout)

        # 行距
        spacing_layout = QHBoxLayout()
        spacing_label = QLabel('行距')
        spacing_label.setFixedWidth(60)
        self._spacing_value_label = QLabel('1.8')
        self._spacing_value_label.setFixedWidth(50)

        self._spacing_slider = QSlider(Qt.Horizontal)
        self._spacing_slider.setRange(12, 30)  # 1.2 ~ 3.0
        self._spacing_slider.setValue(18)
        self._spacing_slider.valueChanged.connect(self._on_spacing_changed)

        spacing_layout.addWidget(spacing_label)
        spacing_layout.addWidget(self._spacing_slider)
        spacing_layout.addWidget(self._spacing_value_label)
        layout.addLayout(spacing_layout)

        # 主题
        theme_label = QLabel('主题')
        theme_label.setFixedWidth(60)

        self._light_btn = QPushButton('☀️ 浅色')
        self._light_btn.setCheckable(True)
        self._dark_btn = QPushButton('🌙 深色')
        self._dark_btn.setCheckable(True)

        self._theme_group = QButtonGroup(self)
        self._theme_group.addButton(self._light_btn)
        self._theme_group.addButton(self._dark_btn)
        self._light_btn.clicked.connect(lambda: self._on_theme_changed('light'))
        self._dark_btn.clicked.connect(lambda: self._on_theme_changed('dark'))

        theme_layout = QHBoxLayout()
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self._light_btn)
        theme_layout.addWidget(self._dark_btn)
        layout.addLayout(theme_layout)

        layout.addStretch()

    def load_settings(self, settings: ReadingSettings):
        """从 ReadingSettings 加载到 UI 控件。"""
        self._font_slider.blockSignals(True)
        self._font_slider.setValue(settings.font_size)
        self._font_value_label.setText(f'{settings.font_size} px')
        self._font_slider.blockSignals(False)

        self._spacing_slider.blockSignals(True)
        self._spacing_slider.setValue(int(settings.line_spacing * 10))
        self._spacing_value_label.setText(f'{settings.line_spacing:.1f}')
        self._spacing_slider.blockSignals(False)

        if settings.theme == 'dark':
            self._dark_btn.setChecked(True)
        else:
            self._light_btn.setChecked(True)

    def _on_font_changed(self, value: int):
        self._font_value_label.setText(f'{value} px')
        self.settings_changed.emit()

    def _on_spacing_changed(self, value: int):
        spacing = value / 10.0
        self._spacing_value_label.setText(f'{spacing:.1f}')
        self.settings_changed.emit()

    def _on_theme_changed(self, theme: str):
        self.settings_changed.emit()

    def get_font_size(self) -> int:
        return self._font_slider.value()

    def get_line_spacing(self) -> float:
        return self._spacing_slider.value() / 10.0

    def get_theme(self) -> str:
        return 'dark' if self._dark_btn.isChecked() else 'light'
