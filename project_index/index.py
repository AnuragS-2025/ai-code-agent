"""High-level wrapper and querying layer for the ProjectIndex structure.

This module defines the public interface for triggering index constructions
and safely navigating the underlying project metadata.
"""

from project_index.models import ModuleInfo, ProjectIndex
from project_index.builder import build_project_index


class ProjectIndexer:
    """A read-only, high-level client interface for accessing project metadata.

    This class decouples the user from the construction details of the index 
    and offers a clean, developer-friendly API for inspection and querying.
    """

    def __init__(self) -> None:
        """Initializes an empty ProjectIndexer instance."""
        self._index: ProjectIndex = ProjectIndex()

    def build(self, root: str) -> None:
        """Triggers a full project scan and build, replacing the current index.

        Args:
            root: The directory path where the indexing should commence.
        """
        self._index = build_project_index(root)

    def get_module(self, path: str) -> ModuleInfo | None:
        """Retrieves metadata for a specific module by its absolute path.

        Args:
            path: The absolute path string of the requested module.

        Returns:
            The corresponding ModuleInfo if found, otherwise None.
        """
        return self._index.modules.get(path)

    def list_modules(self) -> list[str]:
        """Returns a list of all indexed module paths."""
        return list(self._index.modules.keys())

    def list_functions(self, module: str) -> list[str]:
        """Lists all top-level functions defined inside a specific module.

        Args:
            module: The absolute path identifier of the target module.

        Returns:
            A list of function name strings. Returns an empty list if the
            module does not exist or has no top-level functions.
        """
        mod_info = self.get_module(module)
        return mod_info.functions if mod_info else []

    def list_classes(self, module: str) -> list[str]:
        """Lists all top-level classes defined inside a specific module.

        Args:
            module: The absolute path identifier of the target module.

        Returns:
            A list of class name strings. Returns an empty list if the
            module does not exist or has no top-level classes.
        """
        mod_info = self.get_module(module)
        return mod_info.classes if mod_info else []

    def list_imports(self, module: str) -> list[str]:
        """Lists all dependencies and packages imported by a specific module.

        Args:
            module: The absolute path identifier of the target module.

        Returns:
            A list of imported module/package names. Returns an empty list if 
            the module does not exist or has no imports.
        """
        mod_info = self.get_module(module)
        return mod_info.imports if mod_info else []