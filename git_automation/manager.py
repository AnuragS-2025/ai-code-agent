"""
High-Level Git Automation Facade Client.

Aggregates operational subprocess methods from the internal core module to present 
a clean, read-heavy interface targeting automation sequence configurations.
"""

from git_automation.models import GitOperationResult, GitStatus
from git_automation import git


class GitAutomationManager:
    """
    High-level transaction manager coordinating transactional states 
    without duplicating direct process calling code profiles.
    """

    def status(self) -> GitStatus:
        """Fetches the comprehensive structural status profile of the repository."""
        return git.get_status()

    def diff(self) -> str:
        """Exposes the raw unified diff text tracking modified fields."""
        return git.get_diff()

    def stage(self, paths: list[str]) -> GitOperationResult:
        """Triggers local index caching tracking updates down onto explicit paths."""
        return git.stage_files(paths)

    def commit(self, message: str) -> GitOperationResult:
        """Finalizes standard staged change arrays down onto local storage tracks."""
        return git.commit_changes(message)

    def current_branch(self) -> str:
        """Returns the absolute symbolic name of the active working repository branch."""
        return git.get_current_branch()

    def has_uncommitted_changes(self) -> bool:
        """Evaluates whether untracked or dirty files require stage coordination hooks."""
        return not git.get_status().clean