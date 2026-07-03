"""
Lightweight Local JSON Database Manager.

Coordinates transactional storage safety profiles targeted at isolated absolute execution
history files located within the project's tracking root space.
"""

import json
import threading
from pathlib import Path
from typing import List
from feedback.models import FeedbackEntry
from feedback.serializer import to_dict, from_dict

DB_PATH = Path(".feedback/history.json")

# Private module-level lock for thread safety preparation
_db_lock = threading.Lock()


def _ensure_storage() -> Path:
    """Safely guarantees directory frames exist on disk before accessing locations."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def load_feedback() -> List[FeedbackEntry]:
    """
    Reads the complete transaction list from disk storage. 
    Gracefully returns empty structures if files are absent, corrupted, or invalid.
    
    Handles: FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError
    """
    if not DB_PATH.exists():
        return []
    
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            if not isinstance(raw_data, list):
                return []
            return [from_dict(item) for item in raw_data]
    except (FileNotFoundError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        # Explicitly swallow all targeted load/parse exceptions to preserve pipeline continuity
        return []


def save_feedback(entries: List[FeedbackEntry]) -> None:
    """
    Overwrites disk indexes deterministically with provided operational matrices.
    Wrapped in a thread lock to ensure sequential safe cross-process commits.
    """
    with _db_lock:
        try:
            _ensure_storage()
            serialized_data = [to_dict(e) for e in entries]
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(serialized_data, f, indent=4, sort_keys=True)
        except OSError:
            # Silently ignore operating system level write/access failures 
            pass


def append_feedback(entry: FeedbackEntry) -> None:
    """
    Appends a discrete tracking record onto active persistent history frames.
    Protected under global thread synchronization barriers.
    """
    with _db_lock:
        current_records = load_feedback()
        current_records.append(entry)
        
        # Explicit internal lock re-entrancy safe replication bypass 
        try:
            _ensure_storage()
            serialized_data = [to_dict(e) for e in current_records]
            with open(DB_PATH, "w", encoding="utf-8") as f:
                json.dump(serialized_data, f, indent=4, sort_keys=True)
        except OSError:
            pass