import textwrap

from project_index.scanner import scan_project
from project_index.parser import parse_module
from project_index.builder import build_project_index
from project_index.index import ProjectIndexer
from project_index.cache import (
    get_cached_index,
    set_cached_index,
    clear_cache,
)


def test_scan_project(tmp_path):
    """Scanner should discover only Python files."""

    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b.py").write_text("print('b')")
    (tmp_path / "notes.txt").write_text("ignore me")

    ignored = tmp_path / "__pycache__"
    ignored.mkdir()
    (ignored / "c.py").write_text("print('ignored')")

    files = scan_project(str(tmp_path))

    assert len(files) == 2
    assert any(path.endswith("a.py") for path in files)
    assert any(path.endswith("b.py") for path in files)


def test_parse_module():
    """Parser should extract top-level metadata."""

    import tempfile
    from pathlib import Path

    source = textwrap.dedent(
        """
        import os
        import sys
        from math import sqrt

        GLOBAL = 1

        class Demo:
            def method(self):
                pass

        def foo():
            pass

        async def bar():
            pass
        """
    )

    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "sample.py"
        file.write_text(source)

        module = parse_module(str(file))

        assert "os" in module.imports
        assert "sys" in module.imports
        assert "math" in module.imports

        assert "foo" in module.functions
        assert "bar" in module.functions

        assert "Demo" in module.classes

        assert "GLOBAL" in module.globals


def test_parse_invalid_python():
    """Parser should never crash on invalid syntax."""

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        file = Path(tmp) / "bad.py"
        file.write_text("def broken(:\n")

        module = parse_module(str(file))

        assert module.functions == []
        assert module.classes == []
        assert module.imports == []


def test_build_project_index(tmp_path):
    """Builder should index every discovered module."""

    (tmp_path / "one.py").write_text("x = 1")
    (tmp_path / "two.py").write_text("y = 2")

    index = build_project_index(str(tmp_path))

    assert len(index.modules) == 2


def test_project_indexer(tmp_path):
    """ProjectIndexer wrapper should expose metadata APIs."""

    source = textwrap.dedent(
        """
        import os

        class User:
            pass

        def hello():
            pass
        """
    )

    file = tmp_path / "demo.py"
    file.write_text(source)

    indexer = ProjectIndexer()
    indexer.build(str(tmp_path))

    modules = indexer.list_modules()

    assert len(modules) == 1

    module = modules[0]

    assert "User" in indexer.list_classes(module)
    assert "hello" in indexer.list_functions(module)
    assert "os" in indexer.list_imports(module)


def test_cache():
    """Cache should store and clear ProjectIndex safely."""

    clear_cache()

    assert get_cached_index() is None

    index = build_project_index(".")

    set_cached_index(index)

    assert get_cached_index() is index

    clear_cache()

    assert get_cached_index() is None