"""Project Indexing Package.

Provides clean abstractions to scan, parse, build, cache, and navigate 
immutable Python project metadata structures.
"""

from project_index.models import ModuleInfo, ProjectIndex
from project_index.builder import build_project_index
from project_index.index import ProjectIndexer

__all__ = [
    "ProjectIndexer",
    "build_project_index",
    "ProjectIndex",
    "ModuleInfo",
]