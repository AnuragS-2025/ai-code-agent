"""
Git Automation System Data Models.

Provides immutable, frozen dataclasses to represent the internal state, 
operational results, and transaction records of Git repository interactions.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GitStatus:
    """
    Represents the active working tree status of a Git repository.

    Attributes:
        branch (str): The name of the currently active local branch.
        clean (bool): True if there are no untracked or modified files in the working tree.
        modified_files (list[str]): List of paths with uncommitted or untracked changes.
    """
    branch: str
    clean: bool
    modified_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GitOperationResult:
    """
    Encapsulates the immediate result of a executed low-level Git operation.

    Attributes:
        success (bool): Flag indicating if the execution finished with a zero exit status.
        message (str): Explanatory summary message describing the execution result.
        output (str): Captured plaintext standard output or standard error data combined.
    """
    success: bool
    message: str
    output: str


@dataclass(frozen=True)
class GitCommit:
    """
    Represents a permanent structural commit reference object inside the Git graph.

    Attributes:
        message (str): The complete plaintext message describing the commit change scope.
        branch (str): The branch target where the transaction record was committed.
        commit_hash (str): Unique SHA-1 identifier string of the produced commit.
    """
    message: str
    branch: str
    commit_hash: str