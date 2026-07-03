from typing import Any, List, Set, Dict
from .models import ContextResult
from .graph import _get_attr
from .analyzer import find_related_modules


def resolve_context(module: Any, index: Any, graph: Dict[str, Set[str]]) -> ContextResult:
    """
    Resolves the environmental and symbol context for a given module.
    
    Uses pre-built dependency graph state to avoid redundant performance 
    recomputations on heavy project index instances.
    """
    if not module:
        return ContextResult(module="", related_modules=[], imports=[], exports=[])

    # 1. Resolve current module path
    module_path = _get_attr(module, "path", "")
    if not isinstance(module_path, str):
        module_path = ""

    # 2. Resolve imported modules
    raw_imports = _get_attr(module, "imports", [])
    imports_set: Set[str] = set()
    if isinstance(raw_imports, (list, set, tuple)):
        imports_set = {imp for imp in raw_imports if isinstance(imp, str)}

    # 3. Derive exported symbols dynamically
    exports_set: Set[str] = set()
    for attr_name in ("functions", "classes", "globals"):
        symbols = _get_attr(module, attr_name, [])
        if isinstance(symbols, (list, set, tuple)):
            for sym in symbols:
                if isinstance(sym, str):
                    exports_set.add(sym)

    # 4. Resolve related modules via cached graph instance passed from context manager
    related_modules: List[str] = []
    if module_path and graph:
        related_modules = find_related_modules(module_path, graph)

    return ContextResult(
        module=module_path,
        related_modules=related_modules, 
        imports=sorted(list(imports_set)),
        exports=sorted(list(exports_set))
    )