"""Orchestrates the discovery and parsing of a project to build an index.

This module wires together the scanning logic and the AST parser to construct
a comprehensive, immutable snapshot of the project's metadata.
"""

from project_index.models import ProjectIndex
from project_index.scanner import scan_project
from project_index.parser import parse_module


def build_project_index(root: str) -> ProjectIndex:
    """Scans and parses a project directory to generate an immutable ProjectIndex.

    This function performs a full, fresh traversal of the filesystem from the 
    specified root, filters out ignored directories, parses discovered Python 
    files via AST, and encapsulates the metadata into a single ProjectIndex instance.

    Args:
        root: The absolute or relative path to the root of the project.

    Returns:
        A completely constructed, immutable ProjectIndex object.
    """
    # 1. Discover all Python files deterministically
    file_paths = scan_project(root)

    # 2. Parse every Python file into its metadata representation
    modules_map = {}
    for path in file_paths:
        modules_map[path] = parse_module(path)

    # 3. Encapsulate into an immutable index container
    return ProjectIndex(modules=modules_map)