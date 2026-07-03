# tests/test_context_engine.py

from context_engine.graph import build_dependency_graph
from context_engine.analyzer import find_related_modules
from context_engine.resolver import resolve_context
from context_engine.context import ContextEngine


# ----------------------------------------------------------------------
# Lightweight Mock Objects
# ----------------------------------------------------------------------

class MockModule:
    def __init__(
        self,
        path,
        imports=None,
        functions=None,
        classes=None,
        globals=None,
    ):
        self.path = path
        self.imports = imports or []
        self.functions = functions or []
        self.classes = classes or []
        self.globals = globals or []


class MockProjectIndex:
    def __init__(self, modules):
        self.modules = modules


# ----------------------------------------------------------------------
# Graph Tests
# ----------------------------------------------------------------------

def test_empty_graph():
    index = MockProjectIndex({})

    graph = build_dependency_graph(index)

    assert graph == {}


def test_single_module_graph():
    module = MockModule(
        path="a.py",
        imports=[],
    )

    index = MockProjectIndex(
        {
            "a.py": module,
        }
    )

    graph = build_dependency_graph(index)

    assert graph == {
        "a.py": set()
    }


def test_two_module_graph():
    a = MockModule(
        path="a.py",
        imports=["b.py"],
    )

    b = MockModule(
        path="b.py",
        imports=[],
    )

    index = MockProjectIndex(
        {
            "a.py": a,
            "b.py": b,
        }
    )

    graph = build_dependency_graph(index)

    assert graph["a.py"] == {"b.py"}
    assert graph["b.py"] == set()


# ----------------------------------------------------------------------
# Analyzer Tests
# ----------------------------------------------------------------------

def test_find_related_modules():
    graph = {
        "a.py": {"b.py"},
        "b.py": set(),
    }

    related = find_related_modules("a.py", graph)

    assert related == ["b.py"]


def test_circular_dependency():
    graph = {
        "a.py": {"b.py"},
        "b.py": {"a.py"},
    }

    related = find_related_modules("a.py", graph)

    assert related == ["b.py"]


def test_unknown_module():
    graph = {
        "a.py": {"b.py"},
    }

    assert find_related_modules("missing.py", graph) == []


# ----------------------------------------------------------------------
# Resolver Tests
# ----------------------------------------------------------------------

def test_resolver():
    module = MockModule(
        path="a.py",
        imports=["b.py"],
        functions=["foo"],
        classes=["Bar"],
        globals=["VALUE"],
    )

    graph = {
        "a.py": {"b.py"},
        "b.py": set(),
    }

    result = resolve_context(
        module,
        None,
        graph,
    )

    assert result.module == "a.py"

    assert result.imports == ["b.py"]

    assert sorted(result.exports) == [
        "Bar",
        "VALUE",
        "foo",
    ]

    assert result.related_modules == ["b.py"]


# ----------------------------------------------------------------------
# Context Engine Tests
# ----------------------------------------------------------------------

def test_context_engine():
    a = MockModule(
        path="a.py",
        imports=["b.py"],
        functions=["run"],
    )

    b = MockModule(
        path="b.py",
    )

    index = MockProjectIndex(
        {
            "a.py": a,
            "b.py": b,
        }
    )

    engine = ContextEngine()

    engine.build(index)

    context = engine.get_context("a.py")

    assert context.module == "a.py"

    assert context.imports == ["b.py"]

    assert context.related_modules == ["b.py"]

    assert context.exports == ["run"]

    assert engine.get_related_modules("a.py") == ["b.py"]