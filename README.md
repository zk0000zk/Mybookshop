# 电子书阅读器 — 产品文档

> 一款面向个人阅读场景的桌面电子书阅读器，支持 EPUB / TXT 格式，提供书架管理、续读、书内搜索和个性化阅读设置。

## 1. 产品简介

本产品是一款本地桌面电子书阅读器，核心目标是让用户在不需要注册和联网的前提下，完成"导入一本书、阅读内容、下次继续阅读"的完整闭环。

- **技术栈**：Python 3.10+ / PySide6 (Qt) / EbookLib / SQLite
- **支持格式**：EPUB、TXT
- **数据存储**：本地 SQLite，所有数据仅在本地处理，不上传网络
- **适用平台**：Windows / macOS / Linux（需 Python 3.10+ 环境）

---

## 2. 功能列表

### 2.1 书架管理

| 功能 | 说明 |
|------|------|
| 导入书籍 | 支持多选导入 EPUB / TXT 文件，自动解析书名、作者、章节数、文件大小等元数据 |
| 书架展示 | 网格布局展示书籍卡片，每张卡片显示书名、作者、最近阅读时间和阅读进度条 |
| 书名搜索 | 顶部搜索框实时筛选书架中的书籍（按书名或作者匹配） |
| 删除书籍 | 右键菜单移除书架记录（仅删除应用内记录，不删除用户的原始文件） |
| 空状态 | 书架为空时居中提示"导入本地书籍"，引导用户操作 |
| 文件检测 | 打开书籍时检测原始文件是否存在，若文件被移动或删除则提示并提供移除记录选项 |

### 2.2 阅读器

| 功能 | 说明 |
|------|------|
| 内容渲染 | 使用 QTextBrowser 渲染 EPUB (HTML) 和 TXT (纯文本) 内容，注入 CSS 控制字号、行距和主题色 |
| 章节切换 | EPUB 按 spine 顺序加载章节，支持上一章 / 下一章切换；键盘左右方向键或 PageUp/PageDown 翻章 |
| 进度条 | 底部显示全书阅读百分比，实时随章节切换更新 |
| 自动保存 | 阅读进度自动保存：章节切换时、每 30 秒定时器、返回书架时、窗口关闭时 |
| 续读恢复 | 重新打开书籍时自动恢复到上次阅读的章节和滚动位置 |
| 键盘快捷键 | ← / PageUp 上一章，→ / PageDown 下一章，Esc 返回书架 |

### 2.3 目录面板

| 功能 | 说明 |
|------|------|
| 章节列表 | EPUB 书籍显示完整章节目录，点击章节标题跳转到对应内容 |
| TXT 提示 | TXT 格式无章节目录，面板提示"TXT 文件无目录" |
| 面板切换 | 点击工具栏"目录"按钮切换显示/隐藏，与其他侧边面板互斥 |

### 2.4 书内搜索

| 功能 | 说明 |
|------|------|
| 关键词搜索 | 在当前书籍全部章节中搜索关键词，返回匹配结果列表 |
| 结果展示 | 每条结果显示章节标题和匹配文本片段 |
| 跳转定位 | 点击搜索结果跳转到对应章节 |
| 面板切换 | 点击工具栏"搜索"按钮切换显示/隐藏 |

### 2.5 阅读设置

| 功能 | 说明 |
|------|------|
| 字号调节 | 12px ~ 32px 范围调节 |
| 行距调节 | 1.2 ~ 3.0 倍行距 |
| 主题切换 | 浅色 / 深色主题，即时生效并持久化 |
| 即时预览 | 调整设置后立即重新渲染当前章节，无需手动刷新 |
| 设置持久化 | 所有设置保存在 SQLite，下次启动自动恢复 |

---

## 3. 安装与启动

### 3.1 环境要求

- Python 3.10 或更高版本
- 操作系统：Windows / macOS / Linux

### 3.2 安装依赖

```bash
# 进入项目目录
cd 阅读

# 创建虚拟环境（推荐）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

依赖清单（`requirements.txt`）：

```
PySide6-Essentials>=6.6.0    # Qt GUI 框架（Essentials 版不含 WebEngine，体积更小）
ebooklib>=0.18               # EPUB 文件解析
charset-normalizer>=3.3.0    # TXT 文件编码自动检测
```

> **说明**：本项目使用 `PySide6-Essentials` 而非完整 `PySide6`，因为阅读区使用 QTextBrowser 渲染，不需要 QtWebEngine 组件，安装包从 ~170MB 降至 ~82MB。

### 3.3 启动应用

```bash
python -m src.main
```

或直接运行入口文件：

```bash
python src/main.py
```

首次启动时，应用会在 `~/.mybookshelf/` 目录下自动创建 SQLite 数据库 `data.db`，无需手动配置。

### 3.4 开发依赖（可选）

如需运行测试，额外安装：

```bash
pip install -r requirements-dev.txt
```

开发依赖清单（`requirements-dev.txt`）：

```
pytest>=8.0.0
pytest-qt>=4.4.0
```

---

## 4. 使用指南

### 4.1 导入第一本书

1. 启动应用后，书架为空，页面居中显示提示文字。
2. 点击右上角"导入书籍"按钮。
3. 在文件选择对话框中选择本地 EPUB 或 TXT 文件（支持多选）。
4. 导入成功后，书架以网格卡片形式展示书籍。

### 4.2 开始阅读

1. **双击**书籍卡片，或**右键 → 打开**进入阅读页。
2. 首次打开从第一章开始阅读；再次打开自动恢复到上次位置。
3. 使用键盘 ← / → 或 PageUp / PageDown 切换章节。
4. 按 Esc 或点击工具栏"← 返回书架"退出阅读。

### 4.3 使用目录跳转

1. 点击工具栏"目录"按钮，右侧弹出章节列表面板。
2. 点击章节标题，阅读区跳转到对应章节内容。
3. 再次点击"目录"按钮收起面板。

### 4.4 书内搜索

1. 点击工具栏"搜索"按钮，右侧弹出搜索面板。
2. 在输入框输入关键词，按回车搜索。
3. 结果列表显示匹配的章节标题和文本片段。
4. 点击结果跳转到对应章节。

### 4.5 调整阅读设置

1. 点击工具栏"设置"按钮，右侧弹出设置面板。
2. 调节字号滑块（12~32px）、行距滑块（1.2~3.0）。
3. 点击"浅色"或"深色"切换主题。
4. 所有变更即时生效，无需手动保存。

---

## 5. 系统架构

### 5.1 分层结构

```
┌──────────────────────────────────────────┐
│               UI 层 (PySide6)              │
│  书架页 │ 阅读页 │ 目录面板 │ 搜索面板 │ 设置面板 │
├──────────────────────────────────────────┤
│             业务逻辑层 (Services)            │
│  BookService │ ReadingService │ SettingsService │
├──────────────────────────────────────────┤
│             数据访问层 (Repository)           │
│  BookRepository │ ProgressRepository │ SettingsRepository │
├──────────────────────────────────────────┤
│               存储层 (SQLite)               │
│        books │ reading_progress │ settings │
├──────────────────────────────────────────┤
│             文件解析层 (Parsers)            │
│      EpubParser (EbookLib) │ TxtParser      │
└──────────────────────────────────────────┘
```

### 5.2 设计原则

- **UI 与数据分离**：UI 层只负责展示和交互，不直接操作 SQLite。
- **Service 面向 UI**：每个 UI 页面通过对应的 Service 获取数据，Service 内部调用 Repository。
- **Repository 面向数据**：封装所有 SQL 操作，上层不感知 SQL 细节。
- **Parser 可扩展**：EPUB 和 TXT 各有独立 Parser，后续增加 PDF 只需新增 Parser。

### 5.3 项目结构

```
阅读/
├── src/
│   ├── main.py                     # 应用入口
│   ├── app.py                      # QApplication 初始化
│   ├── ui/                         # UI 层
│   │   ├── main_window.py          # 主窗口（QStackedWidget 页面切换）
│   │   ├── bookshelf/
│   │   │   ├── bookshelf_page.py   # 书架页（网格布局、导入、搜索）
│   │   │   └── book_card.py        # 书籍卡片组件
│   │   ├── reader/
│   │   │   ├── reader_page.py      # 阅读页（渲染、翻页、进度、自动保存）
│   │   │   ├── toc_panel.py        # 目录面板
│   │   │   ├── search_panel.py     # 搜索面板
│   │   │   └── settings_panel.py   # 阅读设置面板
│   │   └── widgets/
│   │       └── empty_state.py      # 空状态提示组件
│   ├── services/                   # 业务逻辑层
│   │   ├── book_service.py         # 导入、删除、列表、文件检测
│   │   ├── reading_service.py      # 打开、进度保存/恢复、搜索
│   │   └── settings_service.py     # 设置管理
│   ├── repository/                 # 数据访问层
│   │   ├── database.py             # SQLite 单例连接管理
│   │   ├── book_repository.py      # 书架 CRUD
│   │   ├── progress_repository.py  # 阅读进度 CRUD
│   │   └── settings_repository.py  # 设置 KV 存储
│   ├── parsers/                    # 文件解析层
│   │   ├── base_parser.py          # Parser 接口 + 数据模型
│   │   ├── epub_parser.py          # EPUB 解析（EbookLib）
│   │   └── txt_parser.py           # TXT 解析（编码检测）
│   └── utils/
│       ├── path_utils.py           # 路径处理、格式化
│       └── text_utils.py           # 文本处理
├── resources/
│   ├── light.qss                   # 浅色主题样式
│   └── dark.qss                    # 深色主题样式
├── tests/                          # 测试（73 个）
│   ├── conftest.py                 # 全局 fixtures
│   ├── test_parsers/               # Parser 层测试（16 个）
│   ├── test_repository/            # Repository 层测试（22 个）
│   ├── test_services/              # Service 层测试（29 个）
│   └── test_ui/                    # UI 层测试（6 个）
├── requirements.txt                # 运行依赖
├── requirements-dev.txt           # 开发依赖
├── pytest.ini                      # pytest 配置
└── PRODUCT_DESIGN.md               # 产品设计文档
```

---

## 6. 数据模型

### 6.1 数据库表

应用使用单个 SQLite 文件 `~/.mybookshelf/data.db`，首次运行自动创建。

#### books — 书架书籍

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 书籍 ID（自增） |
| title | TEXT | 书名 |
| author | TEXT | 作者（可空） |
| file_path | TEXT | 原始文件绝对路径 |
| file_format | TEXT | `epub` / `txt` |
| cover_path | TEXT | 封面图缓存路径（可空） |
| total_chapters | INTEGER | 章节总数 |
| file_size | INTEGER | 文件大小（字节） |
| imported_at | TIMESTAMP | 导入时间 |
| last_read_at | TIMESTAMP | 最近阅读时间（可空） |

#### reading_progress — 阅读进度

| 字段 | 类型 | 说明 |
|------|------|------|
| book_id | INTEGER PK | 关联 books.id（外键级联删除） |
| chapter_index | INTEGER | 当前章节序号 |
| scroll_position | REAL | 章节内滚动位置（0.0~1.0） |
| percentage | REAL | 全书阅读百分比 |
| updated_at | TIMESTAMP | 更新时间 |

#### settings — 阅读设置（KV 结构）

| key | 默认值 | 说明 |
|-----|--------|------|
| font_size | 16 | 字号 (px)，范围 12~32 |
| line_spacing | 1.8 | 行距倍数，范围 1.2~3.0 |
| theme | light | `light` / `dark` |
| page_mode | scroll | `scroll` / `paged` |

---

## 7. 测试

### 7.1 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行全部测试
python -m pytest tests/ -v --tb=short
```

### 7.2 测试覆盖

| 层级 | 测试数 | 覆盖范围 |
|------|--------|----------|
| Parser | 16 | EPUB 元数据解析、章节提取、HTML 清理；TXT 编码检测（UTF-8 / GBK）、章节切分、搜索 |
| Repository | 22 | books CRUD、按时间排序、文件存在检测；进度保存/更新/删除/级联删除；设置 KV 读写/覆盖/默认值 |
| Service | 29 | 导入（TXT/EPUB/不支持格式/不存在文件/重复导入）、删除、列表；打开/进度恢复/搜索/章节获取；设置读写/参数校验/持久化 |
| UI | 6 | 空状态展示、导入后卡片显示、多书导入、搜索过滤、删除刷新、空状态组件 |
| **合计** | **73** | **全部通过** |

---

## 8. 关键设计说明

### 8.1 EPUB 渲染策略

- **MVP 阶段**使用 QTextBrowser 渲染 EPUB 章节内容（HTML），轻量且内置于 Qt，足以完成核心阅读流程。
- 后续可切换到 QWebEngineView（Chromium 内核）以提升复杂 CSS 排版质量。
- 渲染时通过注入 CSS 控制字号、行距和主题色，实现设置即时生效。

### 8.2 TXT 编码检测

- 使用 `charset-normalizer` 库自动检测 TXT 文件编码（UTF-8、GBK、BIG5 等）。
- TXT 文件不分章，整体作为一个 Chapter 处理。
- 书名取文件名（去掉扩展名），作者为空。

### 8.3 进度保存机制

- 阅读进度以 `book_id` 为主键，一本书最多一条进度记录。
- 进度包含 `chapter_index`（章节序号）和 `scroll_position`（章节内滚动比例 0.0~1.0）。
- 保存时机：章节切换、每 30 秒定时器、返回书架、窗口关闭。
- 删除书籍时级联删除进度记录（SQLite 外键 `ON DELETE CASCADE`）。

### 8.4 主题实现

- 全局 UI 主题使用 QSS（Qt Style Sheet），两套文件：`resources/light.qss` 和 `resources/dark.qss`。
- 阅读区主题通过注入 CSS 到渲染内容实现：

```css
/* 浅色 */
body { background: #ffffff; color: #333333; }

/* 深色 */
body { background: #1e1e1e; color: #d4d4d4; }
```

- 切换主题时调用 `QApplication.setStyleSheet()` 全局替换，同时重新渲染当前章节内容。

### 8.5 数据安全

- 所有书籍内容和用户数据仅在本地处理，不上传到网络。
- 删除书架书籍只删除应用内数据库记录，不删除用户的原始电子书文件。
- 数据库存储在用户主目录 `~/.mybookshelf/data.db`。

---

## 9. 后续迭代方向

在 MVP 获得稳定使用反馈后，可依次评估：

- 阅读笔记与划线功能
- PDF 格式支持
- 书籍元数据编辑
- EPUB 渲染切换为 QWebEngineView
- 云端同步与跨设备阅读
- AI 辅助阅读功能

是否推进这些能力，应以用户对本地阅读核心体验的真实使用数据为依据。
