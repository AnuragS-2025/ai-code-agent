"""Validation Engine Package API.

This package exposes the public entry points for the Patch Validation Engine,
providing structures and managers to sequentially verify patch payloads.
"""

from validation.models import ValidationStage, ValidationReport
from validation.manager import ValidationManager

__all__ = [
    "ValidationStage",
    "ValidationReport",
    "ValidationManager",
]