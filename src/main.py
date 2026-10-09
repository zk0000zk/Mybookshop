"""应用入口：QApplication 初始化与启动。"""
from __future__ import annotations

import sys
import os


def main():
    # 确保项目根目录在 sys.path 中
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from src.ui.main_window import MainWindow

    # 高 DPI 支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName('MyBookshelf')

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
