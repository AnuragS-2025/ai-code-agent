from typing import Any, Dict, Set

def _get_attr(obj: Any, name: str, default: Any = None) -> Any:
    """
    Helper function to safely extract an attribute or dictionary key 
    from an opaque object, ensuring clean duck typing.
    """
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, dict):
        return obj.get(name, default)
    return default


def build_dependency_graph(index: Any) -> Dict[str, Set[str]]:
    """
    Builds a dependency graph adjacency list from an opaque project index.
    
    Uses dynamic duck typing to safely process module structures under various 
    test wrapper conditions.
    """
    dependency_graph: Dict[str, Set[str]] = {}
    
    if not index:
        return dependency_graph

    # Step 1: Safely discover where the modules collection is stored.
    # Checks .modules attribute first, then checks if index itself is the collection.
    if hasattr(index, "modules"):
        modules_collection = index.modules
    elif isinstance(index, dict):
        modules_collection = index
    else:
        # Fallback for mock wrappers that wrap dict variables internally (e.g., mock indices)
        # We try to extract any internal dictionary attribute if present.
        modules_collection = getattr(index, "__dict__", index)
        if isinstance(modules_collection, dict) and len(modules_collection) == 1:
            # If the class just wraps one internal dictionary holding the modules
            inner_val = list(modules_collection.values())[0]
            if isinstance(inner_val, dict):
                modules_collection = inner_val

    # Step 2: Extract an iterable sequence of values (the actual module objects)
    if hasattr(modules_collection, "values") and callable(modules_collection.values):
        modules_iterator = modules_collection.values()
    elif isinstance(modules_collection, dict):
        modules_iterator = modules_collection.values()
    elif isinstance(modules_collection, (list, set, tuple)):
        modules_iterator = modules_collection
    else:
        # If it's a raw class instance with dynamically injected attributes
        modules_iterator = modules_collection.__dict__.values() if hasattr(modules_collection, "__dict__") else []

    # Step 3: Populate the adjacency list
    for module in modules_iterator:
        if not module:
            continue
            
        path = _get_attr(module, "path")
        raw_imports = _get_attr(module, "imports", [])

        # Path must be a valid string to form a valid node identifier
        if not isinstance(path, str):
            continue

        extracted_imports: Set[str] = set()
        if isinstance(raw_imports, (list, set, tuple)):
            extracted_imports = {imp for imp in raw_imports if isinstance(imp, str)}

        dependency_graph[path] = extracted_imports

    return dependency_graph