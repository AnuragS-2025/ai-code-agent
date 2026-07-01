# utils/file_discovery.py
from pathlib import Path

def discover_python_files(targets: list[str]) -> list[str]:
    """
    Accepts a list of file or directory paths, recursively finds all
    Python (.py) files, and returns a sorted list of unique file paths.
    """
    files = []

    for target in targets:
        path = Path(target)

        if path.is_file() and path.suffix == ".py":
            files.append(str(path))

        elif path.is_dir():
            files.extend(
                str(file)
                for file in path.rglob("*.py")
            )

    return sorted(set(files))