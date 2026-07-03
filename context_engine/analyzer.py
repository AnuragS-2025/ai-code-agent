from typing import Dict, Set, List

def find_related_modules(module: str, graph: Dict[str, Set[str]]) -> List[str]:
    """
    Finds all directly connected neighboring modules for a given target module.
    
    This function performs pure memory-based graph analysis. It does not recurse,
    does not run DFS/BFS algorithms, and does not touch the filesystem.
    
    A module is considered related if:
    1. It is imported by the target module (Outgoing dependency).
    2. It imports the target module (Incoming dependency).
    
    Args:
        module (str): The name/path of the target module.
        graph (Dict[str, Set[str]]): The dependency graph represented as an adjacency list.
        
    Returns:
        List[str]: A deterministically sorted list of all unique immediate neighbors.
    """
    if not graph or module not in graph:
        return []

    related_modules: Set[str] = set()

    # 1. Outgoing Dependencies: Modules that our target module directly imports
    # Since graph is dict[str, set[str]], graph[module] gives us outgoing edges directly.
    related_modules.update(graph[module])

    # 2. Incoming Dependencies: Modules that directly import our target module
    for source_module, imported_set in graph.items():
        if module in imported_set:
            related_modules.add(source_module)

    # Clean up self-references if a module accidentally imports itself
    if module in related_modules:
        related_modules.remove(module)

    # Deterministic output guarantee via alphabetical sorting
    return sorted(list(related_modules))