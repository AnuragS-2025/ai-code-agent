"""
Feedback Data Models Module.

This module provides immutable, thread-safe data representations for tracking 
and profiling auto-fix pipeline execution actions across discrete rules and files.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class FeedbackEntry:
    """
    An immutable record representing the outcome of an automated patch application.

    Attributes:
        rule (str): The unique Identifier string of the static analysis rule (e.g., 'B307').
        file (str): The absolute normalized structural storage path of the file targeted.
        success (bool): Flag indicating whether the generated patch successfully cleared issues.
        iteration (int): The loop iteration window index during which this execution occurred.
        message (str): Explanatory analysis logs or structural validation constraint descriptions.
        timestamp (str): ISO 8601 string representing precisely when the record was compiled (Timezone Aware).
    """
    rule: str
    file: str
    success: bool
    iteration: int
    message: str
    # FIXED: Replaced deprecated datetime.utcnow() with explicit future-proof timezone.utc object
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())