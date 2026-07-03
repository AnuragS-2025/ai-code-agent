"""AST parsing utilities for extracting module metadata.

This module analyzes Python source files using the Abstract Syntax Tree (AST) 
to extract top-level imports, functions, classes, and global assignments 
without executing the code.
"""

import ast
from pathlib import Path
from project_index.models import ModuleInfo


def parse_module(file_path: str) -> ModuleInfo:
    """Parses a Python file to extract its top-level definitions and imports.

    This function reads the file and builds an AST. It extracts top-level items 
    while ignoring nested definitions (e.g., functions inside functions, or 
    methods inside classes). If the file contains invalid Python syntax or 
    cannot be read, it returns an empty ModuleInfo object to avoid crashing.

    Args:
        file_path: The absolute or relative path to the Python source file.

    Returns:
        A ModuleInfo instance containing lists of identified top-level elements.
    """
    path_obj = Path(file_path)
    
    # Initialize empty lists for the final ModuleInfo metadata
    imports: list[str] = []
    functions: list[str] = []
    classes: list[str] = []
    globals_: list[str] = []

    try:
        source = path_obj.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path_obj))
    except (SyntaxError, ValueError, OSError, UnicodeDecodeError):
        # Gracefully handle compilation errors, bad encodings, or missing files
        return ModuleInfo(path=str(path_obj))

    # Iterate strictly over the top-level nodes of the AST
    for node in tree.body:
        
        # 1. Handle Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # Formats as 'module.submodule' or 'module' if level/module names exist
            module_name = node.module if node.module else ""
            imports.append(module_name)

        # 2. Handle Functions
        elif isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)

        # 3. Handle Classes
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        # 4. Handle Global Variables (Assignments at the root level)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    globals_.append(target.id)
                elif isinstance(target, ast.Tuple) or isinstance(target, ast.List):
                    # Unpacks target elements for multi-assignments like: x, y = 1, 2
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            globals_.append(elt.id)
                            
        elif isinstance(node, ast.AnnAssign):
            # Handles annotated assignments like: x: int = 1
            if isinstance(node.target, ast.Name):
                globals_.append(node.target.id)

    return ModuleInfo(
        path=str(path_obj),
        imports=sorted(list(set(imports))),
        functions=functions,
        classes=classes,
        globals=globals_,
    )