"""
Public Feedback Layer Interface.

Exposes only the explicit management client abstractions and structured data model
definitions needed for standard external operational interactions.
"""

from feedback.models import FeedbackEntry
from feedback.manager import FeedbackManager

__all__ = ["FeedbackEntry", "FeedbackManager"]