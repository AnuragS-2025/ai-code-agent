"""
JSON Serialization Layer.

Provides deterministic data translation utilities mapping immutable domain models 
into standard JSON-compatible Python dictionaries without introducing side effects.
"""

from typing import Any, Dict
from feedback.models import FeedbackEntry


def to_dict(entry: FeedbackEntry) -> Dict[str, Any]:
    """
    Converts a FeedbackEntry record into a deterministic, JSON-compatible dictionary.
    """
    return {
        "rule": entry.rule,
        "file": entry.file,
        "success": entry.success,
        "iteration": entry.iteration,
        "message": entry.message,
        "timestamp": entry.timestamp
    }


def from_dict(data: Dict[str, Any]) -> FeedbackEntry:
    """
    Reconstructs a valid FeedbackEntry record from a structured dictionary layer.
    """
    return FeedbackEntry(
        rule=str(data["rule"]),
        file=str(data["file"]),
        success=bool(data["success"]),
        iteration=int(data["iteration"]),
        message=str(data["message"]),
        timestamp=str(data["timestamp"])
    )