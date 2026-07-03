"""Filesystem scanning utilities for Python projects.

This module provides high-performance, deterministic discovery of Python source 
files within a project directory, while automatically ignoring common build, 
virtual environment, cache, and version control directories.
"""

from pathlib import Path

# A set of directory names to strictly ignore during recursive scanning.
# Using a set provides O(1) lookups for performance during filesystem traversal.
DEFAULT_IGNORE_DIRS: set[str] = {
    "__pycache__",
    ".git",
    "venv",
    ".env",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}


def scan_project(root: str) -> list[str]:
    """Recursively discovers all Python source files under the given root directory.

    This function traverses the directory tree, filters out common noise directories
    (such as virtual environments, caches, and build artifacts), and returns the
    absolute paths of all discovered '.py' files in a deterministic, sorted order.

    Args:
        root: The path to the root directory of the project to scan.

    Returns:
        A sorted list of absolute string paths to the discovered Python source files.
        Returns an empty list if the root path does not exist or contains no matching files.

    Raises:
        TypeError: If the provided root is not a string.
    """
    if not isinstance(root, str):
        raise TypeError("Project root path must be a string.")

    root_path = Path(root).resolve()
    if not root_path.exists() or not root_path.is_dir():
        return []

    python_files: list[str] = []

    def _walk(current_dir: Path) -> None:
        try:
            # Iterate through the directory contents exactly once
            for item in current_dir.iterdir():
                if item.is_dir():
                    # Prune the traversal early if the directory is in the ignore list
                    if item.name not in DEFAULT_IGNORE_DIRS:
                        _walk(item)
                elif item.is_file() and item.suffix == ".py":
                    python_files.append(str(item.absolute()))
        except PermissionError:
            # Gracefully skip directories where the process lacks read permissions
            pass

    _walk(root_path)

    # Sort the list to guarantee deterministic output across different systems/runs
    python_files.sort()
    return python_files