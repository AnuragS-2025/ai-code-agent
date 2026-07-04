"""
Low-Level Git Subprocess Wrapper.

Provides foundational commands that map directly to systemic git operations using 
isolated subprocess runs, ensuring shell safety layers are strictly maintained.
"""

import subprocess
from git_automation.models import GitOperationResult, GitStatus


def run_git_command(args: list[str]) -> GitOperationResult:
    """
    Executes a direct raw git terminal command array securely using subprocess.run.
    Guarantees shell=False is strictly enforced to prevent injection profiles.
    """
    command = ["git"] + args
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            check=False
        )
        
        success = result.returncode == 0
        output = result.stdout if success else result.stderr
        message = f"Command '{' '.join(command)}' completed successfully." if success else f"Command failed with exit code {result.returncode}."
        
        # FIXED: Changed from strip() to rstrip() to preserve leading spaces critical for porcelain mapping
        return GitOperationResult(success=success, message=message, output=output.rstrip())
        
    except (OSError, ValueError) as e:
        return GitOperationResult(
            success=False,
            message=f"Subprocess system runtime failure: {str(e)}",
            output=""
        )


def get_current_branch() -> str:
    """
    Retrieves the name of the currently checked out Git branch.
    Defaults to 'HEAD' if a descriptive pointer cannot be located.
    """
    res = run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
    return res.output if res.success else "HEAD"


def get_status() -> GitStatus:
    """
    Queries porcelain state structures to assess working directory clean indices.
    """
    branch = get_current_branch()
    res = run_git_command(["status", "--porcelain"])
    
    if not res.success:
        return GitStatus(branch=branch, clean=False, modified_files=[])
        
    if not res.output.strip():
        return GitStatus(branch=branch, clean=True, modified_files=[])
        
    modified = []
    for line in res.output.splitlines():
        # --porcelain format guarantees: XY PATH or XY "PATH"
        # Where X and Y are status indicators (including spaces). The path starts at index 3.
        if len(line) > 3:
            file_path = line[3:].strip().strip('"')
            if file_path:
                modified.append(file_path)
            
    return GitStatus(branch=branch, clean=False, modified_files=modified)


def get_diff() -> str:
    """
    Returns the unstructured plaintext unified diff of active modified changes.
    """
    res = run_git_command(["diff"])
    return res.output if res.success else ""


def stage_files(paths: list[str]) -> GitOperationResult:
    """
    Stages specific relative file layout indexes down onto the index target space.
    """
    if not paths:
        return GitOperationResult(success=True, message="No files supplied for staging bounds.", output="")
    return run_git_command(["add"] + paths)


def commit_changes(message: str) -> GitOperationResult:
    """
    Commits staged system changes into a permanent transaction block frame.
    """
    if not message.strip():
        return GitOperationResult(success=False, message="Commit execution blocked: message payload is empty.", output="")
    return run_git_command(["commit", "-m", message])