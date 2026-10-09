"""文件路径处理工具。"""
from __future__ import annotations

import os


def get_data_dir() -> str:
    """获取应用数据目录 (~/.mybookshelf/)，不存在则创建。"""
    data_dir = os.path.join(os.path.expanduser('~'), '.mybookshelf')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_path() -> str:
    """获取数据库文件路径。"""
    return os.path.join(get_data_dir(), 'data.db')


def get_resource_path(relative_path: str) -> str:
    """获取资源文件绝对路径（resources/ 目录下）。"""
    # 从 src/utils/path_utils.py 向上找到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(project_root, relative_path)


def format_file_size(size_bytes: int) -> str:
    """将字节数格式化为可读字符串。"""
    if size_bytes < 1024:
        return f'{size_bytes} B'
    elif size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    elif size_bytes < 1024 * 1024 * 1024:
        return f'{size_bytes / (1024 * 1024):.1f} MB'
    else:
        return f'{size_bytes / (1024 * 1024 * 1024):.2f} GB'


def format_datetime(dt_str: str | None) -> str:
    """格式化时间戳字符串为简短显示。"""
    if not dt_str:
        return '未读'
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(dt_str)
        now = datetime.now()
        if dt.date() == now.date():
            return f'今天 {dt.strftime("%H:%M")}'
        elif (now - dt).days == 1:
            return f'昨天 {dt.strftime("%H:%M")}'
        else:
            return dt.strftime('%m-%d %H:%M')
    except (ValueError, TypeError):
        return '未读'
