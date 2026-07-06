"""Business logic abstractions and orchestration layers for the API.

Handles localized code file identification and sequentially orchestrates
static diagnostic scanners with deduplication, performance optimization, and error tracing.
"""

import csv
import json
import os
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