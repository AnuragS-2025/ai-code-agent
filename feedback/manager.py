"""
Central Feedback Pipeline Orchestrator.

Exposes thread-safe recording commands used directly by external execution logic
to feed tracking state history structures downward into persistent layers.
"""

from typing import List
from feedback.models import FeedbackEntry
from feedback import database


class FeedbackManager:
    """
    Read-only public management abstraction coordinating system action profiling records.
    """
    
    def record_success(self, rule: str, file: str, iteration: int, message: str = "Success") -> FeedbackEntry:
        """Records a successful issue mitigation operation down into local disk structures."""
        entry = FeedbackEntry(
            rule=rule,
            file=file,
            success=True,
            iteration=iteration,
            message=message
        )
        database.append_feedback(entry)
        return entry

    def record_failure(self, rule: str, file: str, iteration: int, message: str) -> FeedbackEntry:
        """Records a validation or application execution fault condition frame."""
        entry = FeedbackEntry(
            rule=rule,
            file=file,
            success=False,
            iteration=iteration,
            message=message
        )
        database.append_feedback(entry)
        return entry

    def get_history(self) -> List[FeedbackEntry]:
        """Fetches active execution history logs compiled down across discrete sessions."""
        return database.load_feedback()

    def clear(self) -> None:
        """Wipes tracked interaction records safely to establish blank state baselines."""
        database.save_feedback([])