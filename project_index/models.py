"""Models representing a static index of a Python project's metadata.

This module defines immutable data structures used to store information about
modules, their locations, and the top-level definitions (imports, functions,
classes, and globals) contained within them. 

These models are strictly data containers and do not handle file I/O or parsing.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModuleInfo:
    """Represents indexed metadata for a single Python module.

    Attributes:
        path: The absolute or project-relative file path to the module.
        imports: A list of module names or symbols imported by this module.
        functions: A list of top-level function names defined in the module.
        classes: A list of top-level class names defined in the module.
        globals: A list of top-level global variable names assigned in the module.
    """

    path: str
    imports: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    classes: list[str] = field(default_factory=list)
    globals: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProjectIndex:
    """Represents the complete index of an entire project.

    Attributes:
        modules: A mapping of module identifiers (e.g., fully qualified names 
            or file paths) to their respective ModuleInfo metadata.
    """

    modules: dict[str, ModuleInfo] = field(default_factory=dict)