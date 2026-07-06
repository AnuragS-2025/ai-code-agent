"""Business logic abstractions and orchestration layers for the API.

Handles localized code file identification and sequentially orchestrates
static diagnostic scanners with deduplication, performance optimization, and error tracing.
"""

import csv
from datetime import datetime
import json
import os
import subprocess
import threading
import uuid
from api.models import (
    ScanResponse,
    IssueModel,
    FixResponse,
    ReportResponse,
    ToolSummary,
    JobResponse,
    JobStatus,
    ExportResponse,
    ExportFormat,
    ScanHistoryEntry,
    ScanHistoryResponse,
    ToolInfo,
    SupportedToolsResponse,
    ConfigResponse,
    FixPreviewResponse,
    PreviewIssue,
    DiffLine,
    DiffResponse,
    GitBackupResponse,
)
from analyzers.ruff_runner import run_ruff
from analyzers.bandit_runner import run_bandit
from analyzers.semgrep_runner import run_semgrep
from parsers.ruff_parser import parse_ruff
from parsers.bandit_parser import parse_bandit
from parsers.semgrep_parser import parse_semgrep
from config.settings import settings
from utils.logger import get_logger
from pipeline import run_pipeline

logger = get_logger(__name__)

# Module-level tracking ledger for in-memory background job management
jobs: dict[str, JobResponse] = {}

# Module-level tracking ledger for in-memory historical scan logs
scan_history: list[ScanHistoryEntry] = []


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

        # 8. Store tracking snapshot inside history ledger
        scan_history.append(
            ScanHistoryEntry(
                timestamp=datetime.now().isoformat(),
                project_path=target_path,
                total_issues=len(filtered_issues),
            )
        )

        return ScanResponse(success=True, issues=filtered_issues)

    except Exception as exc:
        logger.exception("Project scan failed catastrophically: %s", str(exc))
        return ScanResponse(success=False, issues=[])


def fix_project(project_path: str) -> FixResponse:
    """Orchestrate the automated correction pipeline for detected engine findings.

    Accepts an isolated targeted filesystem coordinate path context, performs
    existence structural assertions, and securely triggers downstream automated modification.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        FixResponse: Consolidated response metadata documenting applied remediation statistics.
    """
    # Resolve and normalize targeting coordinates safely
    target_path = os.path.normpath(os.path.abspath(project_path))

    # 1. Defensive Path Guardrail Validation
    if not os.path.exists(target_path):
        logger.warning("Project fix aborted | Specified path does not exist: %s", target_path)
        return FixResponse(
            success=False,
            message="Specified project path does not exist.",
            files_modified=0,
            issues_fixed=0,
        )

    try:
        # 2. Build Pipeline Input Targets Array Vector
        target_files = [target_path]
        
        # 3. Synchronously Execute Core Transformation Automation Pipeline Layer
        result = run_pipeline(target_files)
        fixed = result.get("fixed", 0)

        return FixResponse(
            success=True,
            message="Pipeline execution completed successfully.",
            files_modified=fixed,
            issues_fixed=fixed,
        )

    except Exception as exc:
        logger.exception("Project auto-fix generation failed catastrophically: %s", str(exc))
        return FixResponse(
            success=False,
            message="Pipeline execution failed.",
            files_modified=0,
            issues_fixed=0,
        )


def generate_report(project_path: str) -> ReportResponse:
    """Scan a target coordinate context path and compute statistical density metrics.

    Invokes the unified structural scanner layer, builds key counts mapping rule profiles, 
    and classifies findings across Ruff, Bandit, and Semgrep detection tooling.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        ReportResponse: Aggregated overview analytics framework summary payload.
    """
    scan_result = scan_project(project_path)

    if not scan_result.success:
        return ReportResponse(
            success=False,
            total_issues=0,
            by_tool=ToolSummary(ruff=0, bandit=0, semgrep=0),
            by_rule={},
        )

    total_issues = len(scan_result.issues)
    by_rule: dict[str, int] = {}
    
    ruff_count = 0
    bandit_count = 0
    semgrep_count = 0

    ruff_prefixes = ("E", "F", "W", "I", "UP", "N", "PL", "RUF")

    for issue in scan_result.issues:
        rule_tag = issue.rule
        by_rule[rule_tag] = by_rule.get(rule_tag, 0) + 1

        if rule_tag.startswith(ruff_prefixes):
            ruff_count += 1
        elif rule_tag.startswith("B"):
            bandit_count += 1
        else:
            semgrep_count += 1

    return ReportResponse(
        success=True,
        total_issues=total_issues,
        by_tool=ToolSummary(ruff=ruff_count, bandit=bandit_count, semgrep=semgrep_count),
        by_rule=by_rule,
    )


def _run_fix_job(job_id: str, project_path: str) -> None:
    """Execute the automated correction pipeline on a detached worker background thread.

    Mutates state ledger responses across RUNNING, COMPLETED, or FAILED execution life cycles.

    Args:
        job_id (str): The unique transaction tracking identifier.
        project_path (str): The targeted workspace folder filesystem location route.
    """
    jobs[job_id].status = JobStatus.RUNNING
    jobs[job_id].message = "Job is currently executing."

    try:
        fix_result = fix_project(project_path)
        
        if fix_result.success:
            jobs[job_id].status = JobStatus.COMPLETED
            jobs[job_id].message = "Auto-fix completed successfully."
        else:
            jobs[job_id].status = JobStatus.FAILED
            jobs[job_id].message = fix_result.message

    except Exception as exc:
        logger.exception("Async background fix job handling caught an unhandled exception for job %s", job_id)
        jobs[job_id].status = JobStatus.FAILED
        jobs[job_id].message = str(exc)


def start_fix_job(project_path: str) -> JobResponse:
    """Initialize and spawn an asynchronous background processing execution thread.

    Generates distinct cryptographic tokens, builds a tracker wrapper state, and schedules workers.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        JobResponse: Initial tracking container payload context tracking active task state.
    """
    job_id = str(uuid.uuid4())
    
    response = JobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Job queued."
    )
    
    jobs[job_id] = response

    threading.Thread(
        target=_run_fix_job,
        args=(job_id, project_path),
        daemon=True,
    ).start()

    return response


def get_job(job_id: str) -> JobResponse | None:
    """Retrieve an active or archived in-memory worker context representation frame.

    Args:
        job_id (str): The unique transaction tracking identifier token.

    Returns:
        JobResponse | None: The matching job snapshot profile tracking container or None.
    """
    return jobs.get(job_id)


def export_report(project_path: str, export_format: ExportFormat) -> ExportResponse:
    """Generate diagnostic summary metrics and format-serialize analytics data packages to disk.

    Ensures downstream artifact storage structural paths are properly resolved, running explicit
    encodings for file system transport as standard text frames.

    Args:
        project_path (str): Path targeting directory structures or individual modules.
        export_format (ExportFormat): Enum declaration identifying requested output encodings.

    Returns:
        ExportResponse: Tracking summary validating artifact export locations and state summaries.
    """
    try:
        report = generate_report(project_path)

        if not report.success:
            return ExportResponse(
                success=False,
                file_path="",
                format=export_format,
                message="Report generation failed.",
            )

        export_dir = "exports"
        os.makedirs(export_dir, exist_ok=True)

        if export_format == ExportFormat.JSON:
            output_path = os.path.join(export_dir, "report.json")
            with open(output_path, mode="w", encoding="utf-8") as json_file:
                json.dump(report.model_dump(), json_file, indent=4)

        elif export_format == ExportFormat.CSV:
            output_path = os.path.join(export_dir, "report.csv")
            with open(output_path, mode="w", encoding="utf-8", newline="") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Rule", "Count"])
                for rule, count in report.by_rule.items():
                    writer.writerow([rule, count])

        return ExportResponse(
            success=True,
            file_path=output_path,
            format=export_format,
            message="Report exported successfully.",
        )

    except Exception as exc:
        logger.exception(
            "Reporting framework encountered an unhandled error writing serializations to disk: %s",
            str(exc),
        )
        return ExportResponse(
            success=False,
            file_path="",
            format=export_format,
            message="Report export failed.",
        )


def get_scan_history() -> ScanHistoryResponse:
    """Retrieve the unified aggregate history listing all recorded project scan events.

    Returns:
        ScanHistoryResponse: Data payload frame containing chronological scan log collections.
    """
    return ScanHistoryResponse(
        success=True,
        history=scan_history,
    )


def get_supported_tools() -> SupportedToolsResponse:
    """Query configuration instances to resolve dynamic registration profiles for analysis runners.

    Returns:
        SupportedToolsResponse: Structured encapsulation sequence detailing active operational states.
    """
    return SupportedToolsResponse(
        success=True,
        tools=[
            ToolInfo(
                name="Ruff",
                enabled=getattr(settings, "ruff_enabled", True),
            ),
            ToolInfo(
                name="Bandit",
                enabled=getattr(settings, "bandit_enabled", True),
            ),
            ToolInfo(
                name="Semgrep",
                enabled=getattr(settings, "semgrep_enabled", True),
            ),
        ],
    )


def get_config() -> ConfigResponse:
    """Query the runtime configuration profile schema state to evaluate pipeline parameters.

    Returns:
        ConfigResponse: Structured environmental context detailing engine settings.
    """
    return ConfigResponse(
        success=True,
        ai_enabled=getattr(settings, "ai_enabled", True),
        ruff_enabled=getattr(settings, "ruff_enabled", True),
        bandit_enabled=getattr(settings, "bandit_enabled", True),
        semgrep_enabled=getattr(settings, "semgrep_enabled", True),
        semgrep_config_path=getattr(settings, "semgrep_config_path", "p/python"),
        max_iterations=getattr(settings, "max_iterations", 3),
    )


def preview_fixes(project_path: str) -> FixPreviewResponse:
    """Execute a zero-mutation dry-run analysis to generate transformation code structural diff previews.

    Scans the designated path target context using available active analyzer engines, extracts original 
    violating file content string entries, and constructs non-destructive suggestion payloads.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        FixPreviewResponse: Compiled list sequence collecting hypothetical line modification logs.
    """
    try:
        target_path = os.path.normpath(os.path.abspath(project_path))

        if not os.path.exists(target_path):
            logger.warning("Fix preview aborted | Specified target path does not exist: %s", target_path)
            return FixPreviewResponse(success=False, previews=[])

        scan_result = scan_project(project_path)
        if not scan_result.success:
            return FixPreviewResponse(success=False, previews=[])

        preview_list: list[PreviewIssue] = []

        for issue in scan_result.issues:
            try:
                if not os.path.exists(issue.file):
                    preview_list.append(
                        PreviewIssue(
                            file=issue.file,
                            line=issue.line,
                            rule=issue.rule,
                            original="",
                            suggested=f"# Suggested fix for {issue.rule}: ",
                        )
                    )
                    continue

                with open(issue.file, mode="r", encoding="utf-8") as source_file:
                    lines = source_file.readlines()

                # Ensure line boundaries match file array constraints
                if 1 <= issue.line <= len(lines):
                    source_line = lines[issue.line - 1].rstrip("\r\n")
                else:
                    source_line = ""

                preview_list.append(
                    PreviewIssue(
                        file=issue.file,
                        line=issue.line,
                        rule=issue.rule,
                        original=source_line,
                        suggested=f"# Suggested fix for {issue.rule}: {source_line}",
                    )
                )

            except Exception as file_exc:
                logger.warning(
                    "Isolated trace reading error caught; appending safe fallback snapshot for rule %s: %s",
                    issue.rule,
                    str(file_exc),
                )
                preview_list.append(
                    PreviewIssue(
                        file=issue.file,
                        line=issue.line,
                        rule=issue.rule,
                        original="",
                        suggested=f"# Suggested fix for {issue.rule}: ",
                    )
                )
                continue

        return FixPreviewResponse(success=True, previews=preview_list)

    except Exception as exc:
        logger.exception("Dry-run fix preview layer processing caught an unhandled exception: %s", str(exc))
        return FixPreviewResponse(success=False, previews=[])


def generate_diff(project_path: str) -> DiffResponse:
    """Generate line-by-line modification differentials by repurposing dry-run fix preview outputs.

    Validates target filesystems, executes a zero-mutation code scan lifecycle, and extracts 
    before-and-after line transformations mapped explicitly inside localized structural containers.

    Args:
        project_path (str): Path targeting directory structures or individual modules.

    Returns:
        DiffResponse: Consolidated sequence tracking line differential changes calculated over the workspace.
    """
    try:
        target_path = os.path.normpath(os.path.abspath(project_path))

        if not os.path.exists(target_path):
            logger.warning("Diff generation aborted | Specified target path does not exist: %s", target_path)
            return DiffResponse(success=False, diffs=[])

        preview_result = preview_fixes(project_path)
        if not preview_result.success:
            return DiffResponse(success=False, diffs=[])

        diff_list: list[DiffLine] = []

        for item in preview_result.previews:
            diff_list.append(
                DiffLine(
                    line_number=item.line,
                    original=item.original,
                    modified=item.suggested,
                )
            )

        return DiffResponse(success=True, diffs=diff_list)

    except Exception as exc:
        logger.exception("Line differential generator layer encountered an unexpected exception: %s", str(exc))
        return DiffResponse(success=False, diffs=[])


def create_git_backup(project_path: str) -> GitBackupResponse:
    """Commit any outstanding structural workspace alterations to create a safe transactional rollback node.

    Resolves the execution repository target context, verifies standard downstream repository 
    presence frameworks, and triggers synchronized sequential Git environment tracking steps.

    Args:
        project_path (str): Path targeting a workspace repository route or specific source file.

    Returns:
        GitBackupResponse: Consolidated container frame tracking operation status and tracking metadata.
    """
    try:
        # Resolve and normalize targeting coordinates safely
        target_path = os.path.normpath(os.path.abspath(project_path))

        # Resolve parent tracking directory layer if targeting a specific file instance
        if os.path.isfile(target_path):
            repo_dir = os.path.dirname(target_path)
        else:
            repo_dir = target_path

        # Defensive path guardrail validation checks
        if not os.path.exists(repo_dir) or not os.path.isdir(repo_dir):
            return GitBackupResponse(
                success=False,
                message="Project is not a Git repository.",
                commit_hash="",
            )

        # Assert repository state infrastructure marker existence
        git_marker = os.path.join(repo_dir, ".git")
        if not os.path.exists(git_marker):
            return GitBackupResponse(
                success=False,
                message="Project is not a Git repository.",
                commit_hash="",
            )

        # 1. Execute staging phase across all localized modifications
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # 2. Execute tracking snapshot transactional entry commit mapping
        subprocess.run(
            ["git", "commit", "-m", "Auto backup before AI fix"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # 3. Resolve active tracking commit revision reference identification hash token
        rev_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        commit_hash = rev_result.stdout.strip()

        return GitBackupResponse(
            success=True,
            message="Git backup created successfully.",
            commit_hash=commit_hash,
        )

    except Exception as exc:
        logger.exception("Git backup orchestration logic encountered an unhandled execution pipeline exception: %s", str(exc))
        return GitBackupResponse(
            success=False,
            message="Git backup failed.",
            commit_hash="",
        )