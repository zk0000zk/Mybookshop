"""Parser 数据模型：BookMetadata 和 Chapter。"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class BookMetadata:
    """书籍元数据，由 Parser解析后返回。"""
    title: str
    author: str | None = None
    file_path: str = ""
    file_format: str = ""          # "epub" / "txt"
    cover_path: str | None = None
    total_chapters: int = 0
    file_size: int = 0


@dataclass
class Chapter:
    """单章节数据。"""
    index: int
    title: str
    content: str                    # HTML 或纯文本
    is_html: bool = False           # content 是否为 HTML
