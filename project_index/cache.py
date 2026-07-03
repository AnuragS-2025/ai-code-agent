"""In-memory, thread-safe caching system for storing a single ProjectIndex instance.

This module utilizes a standard reentrant synchronization lock (`threading.Lock`)
to ensure accurate, race-condition-free cross-thread reading and writing operations.
"""

from threading import Lock
from project_index.models import ProjectIndex

# Internal global cache storage and its corresponding synchronization lock
_CACHE_LOCK = Lock()
_CACHED_INDEX: ProjectIndex | None = None


def get_cached_index() -> ProjectIndex | None:
    """Safely retrieves the single cached ProjectIndex instance.

    Returns:
        The current ProjectIndex if it has been set, otherwise None.
    """
    with _CACHE_LOCK:
        return _CACHED_INDEX


def set_cached_index(index: ProjectIndex) -> None:
    """Safely saves or overwrites the cached ProjectIndex instance.

    Args:
        index: The new ProjectIndex instance to persist in-memory.
    """
    with _CACHE_LOCK:
        global _CACHED_INDEX
        _CACHED_INDEX = index


def clear_cache() -> None:
    """Safely purges the cache, setting the reference back to None."""
    with _CACHE_LOCK:
        global _CACHED_INDEX
        _CACHED_INDEX = None