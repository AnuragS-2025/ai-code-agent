"""
Public Git Automation API Boundary.

Exposes only explicit management wrappers and structural data models to ensure 
low-level sub-process executors stay isolated from external callers.
"""

from git_automation.models import GitStatus, GitOperationResult, GitCommit
from git_automation.manager import GitAutomationManager

__all__ = [
    "GitAutomationManager",
    "GitStatus",
    "GitCommit",
    "GitOperationResult"
]