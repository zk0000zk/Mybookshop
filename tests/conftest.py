"""pytest 全局 fixtures。"""
import pytest
import os
import tempfile
import zipfile
import sys

# 确保项目根目录在 sys.path 中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.repository.database import Database


# ---------- 最小 EPUB 测试文件内容 ----------
_MIMETYPE = "application/epub+zip"
_OPF = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:title>测试电子书</dc:title>
    <dc:creator>测试作者</dc:creator>
    <dc:identifier id="bookid">test-001</dc:identifier>
    <dc:language>zh-CN</dc:language>
  </metadata>
  <manifest>
    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
    <item id="chapter2" href="chapter2.xhtml" media-type="application/xhtml+xml"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
  </manifest>
  <spine toc="ncx">
    <itemref idref="chapter1"/>
    <itemref idref="chapter2"/>
  </spine>
</package>
"""
_CH1 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>第一章</title></head>
<body>
<h1>第一章 开始</h1>
<p>这是第一章的内容。mykeyword 出现在这里。</p>
<p>第二段文本。</p>
</body>
</html>
"""
_CH2 = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>第二章</title></head>
<body>
<h2>第二章 继续</h2>
<p>第二章的内容，也有 mykeyword。</p>
</body>
</html>
"""
_NCX = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="test-001"/>
  </head>
  <docTitle><text>测试电子书</text></docTitle>
  <navMap>
    <navPoint id="nav1" playOrder="1">
      <navLabel><text>第一章</text></navLabel>
      <content src="chapter1.xhtml"/>
    </navPoint>
    <navPoint id="nav2" playOrder="2">
      <navLabel><text>第二章</text></navLabel>
      <content src="chapter2.xhtml"/>
    </navPoint>
  </navMap>
</ncx>
"""


@pytest.fixture
def temp_db(tmp_path):
    """使用临时内存/文件数据库，测试间互不影响。"""
    db_path = str(tmp_path / 'test_data.db')
    Database.reset_instance()
    db = Database(db_path=db_path)
    yield db
    Database.reset_instance()


@pytest.fixture
def txt_file(tmp_path):
    """创建一个临时 TXT 测试文件（中英文混合）。"""
    content = """第一章 开始

这是测试文本的第一章。This is the first chapter.
Hello World, 你好世界。

第二章 继续

这是第二章的内容。
Searching for keyword: mykeyword.
这里有一个关键词 mykeyword 需要被搜索到。
End of file.
"""
    file_path = tmp_path / 'test_book.txt'
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)


@pytest.fixture
def txt_file_gbk(tmp_path):
    """创建 GBK 编码的 TXT 文件（测试编码检测）。"""
    content = "这是GBK编码的中文文件。\n用于测试编码检测功能。"
    file_path = tmp_path / 'gbk_book.txt'
    file_path.write_bytes(content.encode('gbk'))
    return str(file_path)


@pytest.fixture
def txt_file_big(tmp_path):
    """创建一个较长的 TXT 文件，测试性能。"""
    lines = []
    for i in range(500):
        lines.append(f'第{i+1}行：这是测试内容的第{i+1}行，用于测试较长的文本文件处理能力。')
    content = '\n'.join(lines)
    file_path = tmp_path / 'big_book.txt'
    file_path.write_text(content, encoding='utf-8')
    return str(file_path)


@pytest.fixture
def mini_epub(tmp_path):
    """创建一个最小 EPUB 测试文件。"""
    epub_path = tmp_path / 'test_book.epub'
    with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('mimetype', _MIMETYPE, compress_type=zipfile.ZIP_STORED)
        zf.writestr('META-INF/container.xml',
                    '''<?xml version="1.0" encoding="UTF-8"?>
<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>''')
        zf.writestr('content.opf', _OPF)
        zf.writestr('chapter1.xhtml', _CH1)
        zf.writestr('chapter2.xhtml', _CH2)
        zf.writestr('toc.ncx', _NCX)
    return str(epub_path)
