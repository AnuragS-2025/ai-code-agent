from typing import Any, Dict, List, Set
from .models import ContextResult
from .graph import build_dependency_graph, _get_attr
from .resolver import resolve_context
from .analyzer import find_related_modules


class ContextEngine:
    """
    Orchestrates architectural context and dependency tracking across a project index.
    
    Guarantees strict single-pass graph indexing configurations to prevent 
    redundant performance recalculations during high-frequency module processing.
    """

    def __init__(self) -> None:
        self._index: Any = None
        self._graph: Dict[str, Set[str]] = {}

    def build(self, index: Any) -> None:
        """Populates state and builds the module dependency mapping precisely once."""
        self._index = index
        self._graph = build_dependency_graph(index)

    def get_context(self, module: Any) -> ContextResult:
        """Resolves target context metrics reusing the high-performance memory graph."""
        target_module = module
        if isinstance(module, str) and self._index:
            modules_collection = _get_attr(self._index, "modules", self._index)
            if hasattr(modules_collection, "get"):
                target_module = modules_collection.get(module, module)
            elif isinstance(modules_collection, dict):
                target_module = modules_collection.get(module, module)

        # Optimization fixed: Passing self._graph to prevent structural rebuilding loop
        return resolve_context(target_module, self._index, self._graph)

    def get_related_modules(self, module: str) -> List[str]:
        """Retrieves neighbor nodes efficiently directly from the cached dictionary maps."""
        return find_related_modules(module, self._graph)