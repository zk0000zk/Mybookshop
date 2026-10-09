# 电子书阅读器技术方案

> 基于 [PRODUCT_DESIGN.md](../PRODUCT_DESIGN.md) 的产品设计，本文档定义 MVP 的技术实现方案。

## 1. 技术栈

### 1.1 总览

| 层级 | 技术 | 说明 |
| --- | --- | --- |
| 语言 | Python 3.10+ | 项目主语言 |
| UI 框架 | PySide6 (6.6+) | Qt 官方 Python 绑定，LGPL 授权 |
| EPUB 解析 | EbookLib | 读取 OPF/NCX、提取章节 HTML 和元数据 |
| TXT 读取 | 内置 `open()` + `charset-normalizer` | 自动检测文件编码 |
| 数据存储 | SQLite (`sqlite3` 内置模块) | 书架、阅读进度、设置 |
| EPUB 渲染 | QTextBrowser（初期）→ QWebEngineView（后期） | 分阶段升级渲染质量 |
| TXT 渲染 | QTextBrowser | 轻量够用 |
| 测试 | pytest + pytest-qt | 单元测试与 Qt 组件测试 |
| 打包 | PyInstaller | 最终分发为单文件或单目录 |

### 1.2 选型理由

**为什么选 Python + PySide6：**

- EPUB 本质是 XHTML+CSS 打包，需要解析后渲染，Python 生态有成熟的 EbookLib。
- SQLite 是 Python 内置模块，零额外依赖即可完成数据持久化。
- PySide6 控件丰富，授权为 LGPL，商业使用无障碍。

**EPUB 渲染分阶段策略：**

- **初期（MVP Phase 1-2）：QTextBrowser** — 轻量、内置于 Qt，先跑通完整链路（书架→导入→阅读→续读→设置），验证核心流程。
- **后期（MVP Phase 3+）：QWebEngineView** — EPUB 切换到 Chromium 内核渲染，保证复杂 CSS 排版质量。TXT 继续用 QTextBrowser。

## 2. 系统架构

### 2.1 分层结构

```
┌─────────────────────────────────────────┐
│              UI 层 (PySide6)              │
│  书架页 │ 阅读页 │ 目录面板 │ 搜索面板 │ 设置面板  │
├─────────────────────────────────────────┤
│            业务逻辑层 (Services)           │
│  BookService │ ReadingService │ SettingsService │
├─────────────────────────────────────────┤
│            数据访问层 (Repository)          │
│  BookRepository │ ProgressRepository │ SettingsRepository │
├─────────────────────────────────────────┤
│              存储层 (SQLite)               │
│        books │ reading_progress │ settings │
├─────────────────────────────────────────┤
│            文件解析层 (Parsers)            │
│      EpubParser (EbookLib) │ TxtParser      │
└─────────────────────────────────────────┘
```

### 2.2 设计原则

- **UI 与数据分离**：UI 层只负责展示和交互，不直接操作 SQLite。
- **Service 面向 UI**：每个 UI 页面通过对应的 Service 获取数据，Service 内部调用 Repository。
- **Repository 面向数据**：封装所有 SQL 操作，上层不感知 SQL 细节。
- **Parser 可扩展**：EPUB 和 TXT 各有独立 Parser，后续增加 PDF 只需新增 Parser。

## 3. 项目结构

```
阅读/
├── docs/
│   ├── TECHNICAL_DESIGN.md      # 本文件
│   └── PRODUCT_DESIGN.md       # 产品设计文档（副本/链接）
├── src/
│   ├── __init__.py
│   ├── main.py                  # 应用入口
│   ├── app.py                   # QApplication 初始化、全局配置
│   ├── ui/                      # UI 层
│   │   ├── __init__.py
│   │   ├── main_window.py       # 主窗口（页面切换容器）
│   │   ├── bookshelf/
│   │   │   ├── __init__.py
│   │   │   ├── bookshelf_page.py    # 书架页
│   │   │   └── book_card.py         # 书籍卡片组件
│   │   ├── reader/
│   │   │   ├── __init__.py
│   │   │   ├── reader_page.py       # 阅读页
│   │   │   ├── toc_panel.py         # 目录面板
│   │   │   ├── search_panel.py      # 搜索面板
│   │   │   └── settings_panel.py    # 阅读设置面板
│   │   └── widgets/                 # 通用组件
│   │       ├── __init__.py
│   │       └── empty_state.py        # 空状态提示
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── book_service.py       # 导入、删除、列表
│   │   ├── reading_service.py    # 进度保存/恢复、搜索
│   │   └── settings_service.py   # 阅读设置管理
│   ├── repository/              # 数据访问层
│   │   ├── __init__.py
│   │   ├── database.py          # 连接管理、建表、迁移
│   │   ├── book_repository.py
│   │   ├── progress_repository.py
│   │   └── settings_repository.py
│   ├── parsers/                 # 文件解析层
│   │   ├── __init__.py
│   │   ├── base_parser.py       # Parser 接口
│   │   ├── epub_parser.py       # EPUB 解析（EbookLib）
│   │   └── txt_parser.py        # TXT 解析（编码检测）
│   └── utils/                   # 工具函数
│       ├── __init__.py
│       ├── path_utils.py        # 文件路径处理
│       └── text_utils.py        # 文本处理（分页、搜索）
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest fixtures
│   ├── test_parsers/
│   │   ├── test_epub_parser.py
│   │   └── test_txt_parser.py
│   ├── test_repository/
│   │   ├── test_book_repository.py
│   │   ├── test_progress_repository.py
│   │   └── test_settings_repository.py
│   ├── test_services/
│   │   ├── test_book_service.py
│   │   ├── test_reading_service.py
│   │   └── test_settings_service.py
│   └── test_ui/
│       └── test_bookshelf_page.py
├── AGENTS.md
├── PRODUCT_DESIGN.md
└── requirements.txt
```

## 4. 数据模型

### 4.1 数据库表设计

使用单个 SQLite 文件 `~/.mybookshelf/data.db`（首次运行自动创建）。

#### 表：books（书架书籍）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY AUTOINCREMENT | 书籍 ID |
| title | TEXT NOT NULL | 书名 |
| author | TEXT | 作者（可空） |
| file_path | TEXT NOT NULL | 原始文件绝对路径 |
| file_format | TEXT NOT NULL | 格式：`epub` / `txt` |
| cover_path | TEXT | 封面图缓存路径（可空） |
| total_chapters | INTEGER | 章节总数（EPUB 有，TXT 为 1） |
| file_size | INTEGER | 文件大小（字节） |
| imported_at | TIMESTAMP | 导入时间 |
| last_read_at | TIMESTAMP | 最近阅读时间（可空） |

#### 表：reading_progress（阅读进度）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| book_id | INTEGER PRIMARY KEY | 关联 books.id |
| chapter_index | INTEGER NOT NULL | 当前章节序号 |
| scroll_position | REAL NOT NULL | 章节内滚动位置（0.0~1.0） |
| percentage | REAL | 全书阅读百分比（可空） |
| updated_at | TIMESTAMP | 更新时间 |

#### 表：settings（阅读设置，KV 结构）

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| key | TEXT PRIMARY KEY | 设置键名 |
| value | TEXT | 设置值（JSON 序列化） |

预设键值：

| key | value 默认值 | 说明 |
| --- | --- | --- |
| font_size | 16 | 字号 (px) |
| line_spacing | 1.8 | 行距倍数 |
| theme | light | `light` / `dark` |
| page_mode | scroll | `scroll` / `paged` |

### 4.2 ER 关系

```
books (1) ──── (1) reading_progress
    book_id = reading_progress.book_id
```

一本书最多一条进度记录，删除书籍时级联删除进度。

## 5. 核心模块设计

### 5.1 文件解析层

#### BaseParser（接口）

```python
class BaseParser(ABC):
    @abstractmethod
    def parse_metadata(self, file_path: str) -> BookMetadata:
        """解析书籍元数据：标题、作者、封面、章节数"""

    @abstractmethod
    def get_chapters(self, file_path: str) -> list[Chapter]:
        """获取章节列表：序号、标题、HTML/纯文本内容"""

    @abstractmethod
    def get_chapter_content(self, file_path: str, chapter_index: int) -> str:
        """获取指定章节的渲染内容"""
```

#### EpubParser

- 使用 EbookLib 读取 EPUB（本质是 ZIP）。
- 从 OPF 文件提取元数据（title、author、cover image）。
- 按 spine 顺序读取章节 XHTML，每章为一个 Chapter。
- 封面图片提取后缓存到本地临时目录。

#### TxtParser

- 使用 `charset-normalizer` 检测编码后读取全文。
- 不分章，整体作为一个 Chapter。
- 书名取文件名（去掉扩展名），作者为空。

### 5.2 数据访问层

#### Database

- 单例管理 SQLite 连接。
- 首次运行自动建表。
- 提供 `execute()`、`fetchone()`、`fetchall()` 基础方法。

#### BookRepository

```python
class BookRepository:
    def add(self, metadata: BookMetadata) -> int: ...
    def get_by_id(self, book_id: int) -> Book | None: ...
    def list_all(self) -> list[Book]: ...
    def delete(self, book_id: int) -> None: ...
    def update_last_read_time(self, book_id: int) -> None: ...
    def check_file_exists(self, book_id: int) -> bool: ...
```

#### ProgressRepository

```python
class ProgressRepository:
    def get(self, book_id: int) -> ReadingProgress | None: ...
    def save(self, book_id: int, chapter_index: int, scroll_position: float) -> None: ...
    def delete(self, book_id: int) -> None: ...
```

#### SettingsRepository

```python
class SettingsRepository:
    def get(self, key: str, default: str = "") -> str: ...
    def set(self, key: str, value: str) -> None: ...
    def get_all(self) -> dict[str, str]: ...
```

### 5.3 业务逻辑层

#### BookService

- `import_book(file_path)` — 判断格式 → 调用对应 Parser 解析元数据 → 存入 books 表 → 返回 book_id。
- `remove_book(book_id)` — 删除书架记录 + 进度记录（不删原文件）。
- `get_bookshelf()` — 返回所有书籍列表，按最近阅读时间排序。
- `check_file_available(book_id)` — 检查原始文件是否还存在。

#### ReadingService

- `open_book(book_id)` — 加载书籍 → 查进度 → 调用 Parser 获取章节内容 → 返回初始阅读状态。
- `save_progress(book_id, chapter_index, scroll_position)` — 保存进度 + 更新最近阅读时间。
- `search_in_book(book_id, keyword)` — 遍历章节内容，返回匹配位置列表。

#### SettingsService

- `get_settings()` — 从 Repository 读取全部设置并返回结构化对象。
- `update_setting(key, value)` — 更新单个设置。
- 应用启动时自动加载，变更后即时生效并持久化。

### 5.4 UI 层

#### 主窗口 (MainWindow)

- 使用 QStackedWidget 管理页面切换。
- 维护当前页面状态（书架 / 阅读）。

#### 书架页 (BookshelfPage)

- 网格布局展示书籍卡片（封面、书名、作者、最近阅读时间、进度条）。
- 顶部工具栏：导入按钮、搜索框（书名筛选）。
- 空状态：居中提示"导入本地书籍"。
- 右键菜单：打开、删除。
- 双击书籍 → 切换到阅读页。

#### 阅读页 (ReaderPage)

- 中央区域：渲染引擎（QTextBrowser / QWebEngineView）。
- 底部：进度条 + 百分比 + 章节标题。
- 顶部工具栏（可自动收起）：返回书架、目录、搜索、设置。
- 翻页/滚动交互：支持滚动模式和分页模式（MVP 优先滚动）。
- 进度自动保存：章节切换时、定时器每 30 秒、窗口关闭时。

#### 目录面板 (TocPanel)

- QTreeWidget 展示 EPUB 章节树。
- 点击章节 → 跳转到对应章节。
- TXT 不显示目录面板（或提示"TXT 无目录"）。

#### 搜索面板 (SearchPanel)

- 输入框 + 结果列表。
- 结果显示：章节标题 + 匹配文本片段（高亮）。
- 点击结果 → 跳转到对应位置。

#### 设置面板 (SettingsPanel)

- 字号：滑块或按钮调节（12-32px）。
- 行距：滑块调节（1.2-3.0）。
- 主题：浅色/深色切换按钮。
- 变更即时生效：通过信号通知 ReaderPage 重新渲染。

## 6. 主题实现方案

### 浅色 / 深色主题

使用 Qt Style Sheet (QSS) 实现，两套样式表：

- `resources/light.qss` — 浅色主题
- `resources/dark.qss` — 深色主题

切换时调用 `QApplication.setStyleSheet()` 全局替换。

阅读区域主题通过注入 CSS 到渲染内容实现：

```css
/* 浅色 */
body { background: #ffffff; color: #333333; }

/* 深色 */
body { background: #1e1e1e; color: #d4d4d4; }
```

## 7. 实现计划

按优先级分四个阶段：

### Phase 1：书架与导入（基础闭环）

- [ ] 项目初始化：PySide6 + EbookLib + charset-normalizer 依赖
- [ ] SQLite 数据库建表与连接管理
- [ ] BaseParser / EpubParser / TxtParser
- [ ] BookRepository / BookService
- [ ] BookshelfPage（导入、列表、删除）
- [ ] 空状态提示

### Phase 2：阅读与续读

- [ ] ReaderPage 基础框架（QTextBrowser 渲染）
- [ ] 章节加载与切换
- [ ] ProgressRepository / ReadingService
- [ ] 进度自动保存与恢复
- [ ] 工具栏（返回、收起）

### Phase 3：目录、搜索与设置

- [ ] TocPanel（EPUB 章节跳转）
- [ ] SearchPanel（书内搜索）
- [ ] SettingsPanel（字号、行距、主题）
- [ ] SettingsRepository / SettingsService
- [ ] 设置即时生效与持久化
- [ ] EPUB 渲染切换为 QWebEngineView

### Phase 4：打磨与异常处理

- [ ] 文件不可用检测与提示
- [ ] 导入失败错误处理与提示
- [ ] 滚动 / 分页模式切换
- [ ] 工具栏自动收起
- [ ] PyInstaller 打包

## 8. 测试策略

遵循 AGENTS.md 要求：每次改动后编写/更新测试，交付前确保全部通过。

### 8.1 测试分层

| 层级 | 工具 | 覆盖范围 |
| --- | --- | --- |
| Parser 层 | pytest | EPUB/TXT 元数据解析、章节提取 |
| Repository 层 | pytest + 内存 SQLite | CRUD 操作、级联删除 |
| Service 层 | pytest + mock Repository | 业务逻辑、异常分支 |
| UI 层 | pytest-qt | 页面渲染、交互、信号 |

### 8.2 测试数据

- `tests/fixtures/` 下放置测试用 EPUB 和 TXT 文件。
- EPUB：使用公开领域小书籍（如《爱丽丝梦游仙境》公开 EPUB）。
- TXT：使用中文 + 英文混合短文本，覆盖编码检测。

### 8.3 运行方式

```bash
pytest tests/ -v --tb=short
```

## 9. 依赖清单

```
# requirements.txt
PySide6>=6.6.0
EbookLib>=0.18
charset-normalizer>=3.3.0

# 开发依赖
# requirements-dev.txt
pytest>=8.0.0
pytest-qt>=4.4.0
```

## 10. 开放问题

以下问题在实现过程中需要进一步确认：

1. **EPUB 封面提取**：部分 EPUB 无封面图，需要设计默认占位封面。
2. **大文件 TXT 分页**：超长 TXT（>10MB）一次性加载可能卡顿，需要流式分页策略。
3. **QWebEngineView 打包体积**：切换到 WebEngine 后 PyInstaller 打包体积会显著增大，需评估是否可接受。
4. **多显示器 DPI**：高 DPI 屏幕下字体和布局需要适配，PySide6 默认支持但需验证。
