"""Business logic abstractions and orchestration layers for the API.

Handles localized code file identification and sequentially orchestrates
static diagnostic scanners with deduplication, performance optimization, and error tracing.
"""

import os
from api.models import ScanResponse, IssueModel
from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep
from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def scan_project(project_path: str) -> ScanResponse:
    """Collect Python target modules, invoke static analysis engines, and merge diagnostics.

    Optimizes engine performance by passing directory scopes directly to alleviate
    Windows CLI environment limits, deduplicates items, and balances tracking sequences.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        ScanResponse: Consolidated data structure object frame holding findings.
    """
    # Resolve and normalize targeting coordinates safely
    target_path = os.path.normpath(os.path.abspath(project_path))
    
    # 1. Defensive Path Guardrail Validation
    if not os.path.exists(target_path):
        logger.warning("Project scan aborted | Specified path does not exist: %s", target_path)
        return ScanResponse(success=False, issues=[])

    python_files: list[str] = []

    if os.path.isdir(target_path):
        for root, _, files in os.walk(target_path):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
    elif os.path.isfile(target_path) and target_path.endswith(".py"):
        python_files.append(target_path)

    # 2. Empty Scope Structural Validation
    if not python_files:
        logger.info("Project scan finalized | No Python modules identified inside target: %s", target_path)
        return ScanResponse(success=True, issues=[])

    raw_issues: list[IssueModel] = []

    try:
        # 3. Execute Ruff Pipeline Layer (Passing base path vector)
        if getattr(settings, "ruff_enabled", True):
            ruff_raw = run_ruff(target_path)
            ruff_parsed = parse_ruff(ruff_raw)
            for issue in ruff_parsed:
                raw_issues.append(
                    IssueModel(
                        rule=issue["rule"],
                        message=issue["message"],
                        file=os.path.normpath(os.path.abspath(issue["file"])),
                        line=issue["line"],
                    )
                )

        # 4. Execute Bandit Pipeline Layer (Passing base path vector)
        if getattr(settings, "bandit_enabled", True):
            bandit_raw = run_bandit(target_path)
            bandit_parsed = parse_bandit(bandit_raw)
            for issue in bandit_parsed:
                raw_issues.append(
                    IssueModel(
                        rule=issue["rule"],
                        message=issue["message"],
                        file=os.path.normpath(os.path.abspath(issue["file"])),
                        line=issue["line"],
                    )
                )

        # 5. Execute Semgrep Pipeline Layer (Single Run Project Level Optimization)
        if getattr(settings, "semgrep_enabled", True):
            semgrep_config = getattr(settings, "semgrep_config_path", "p/python")
            semgrep_raw = run_semgrep(target_path, set(), config=semgrep_config)
            semgrep_parsed = parse_semgrep(semgrep_raw)
            for issue in semgrep_parsed:
                raw_issues.append(
                    IssueModel(
                        rule=issue["rule"],
                        message=issue["message"],
                        file=os.path.normpath(os.path.abspath(issue["file"])),
                        line=issue["line"],
                    )
                )

        # 6. Cross-Engine Deduplication Logic Matrix Step
        seen_issues = set()
        filtered_issues: list[IssueModel] = []

        for issue in raw_issues:
            issue_key = (issue.rule, issue.file, issue.line, issue.message)
            if issue_key not in seen_issues:
                seen_issues.add(issue_key)
                filtered_issues.append(issue)

        # 7. Deterministic Sorting Sequence 
        filtered_issues.sort(key=lambda issue: (issue.file, issue.line, issue.rule))

        return ScanResponse(success=True, issues=filtered_issues)

    except Exception as exc:
        logger.exception("Project scan failed catastrophically: %s", str(exc))
        return ScanResponse(success=False, issues=[])