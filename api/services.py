"""Business logic abstractions and orchestration layers for the API.

Handles localized code file identification and sequentially orchestrates
static diagnostic scanners with deduplication, performance optimization, and error tracing.
"""

import csv
from datetime import datetime
import json
import os
import shutil
import subprocess
import threading
from typing import List, Dict
import uuid
import zipfile
from fastapi import UploadFile
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
    ZipUploadResponse,
    HtmlReportResponse,
    GitRollbackResponse,
    ExplainResponse,
    SeverityLevel,
    SeverityIssue,
    SeverityFilterResponse,
    RuleSearchResponse,
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
jobs: Dict[str, JobResponse] = {}

# Module-level tracking ledger for in-memory historical scan logs
scan_history: List[ScanHistoryEntry] = []


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

    python_files: List[str] = []

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

    raw_issues: List[IssueModel] = []

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
        filtered_issues: List[IssueModel] = []

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
    by_rule: Dict[str, int] = {}
    
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

        preview_list: List[PreviewIssue] = []

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

        diff_list: List[DiffLine] = []

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


def upload_zip(file: UploadFile) -> ZipUploadResponse:
    """Receive, validate, store, and extract a compressed file-system workspace data payload.

    Ensures target transport directory schemas are created dynamically on disk, executes filename
    suffix format filtering assertions, and unrolls nested items safely using zipfile utilities.
    Memory efficient chunk-wise copying is used to support large archive files.

    Args:
        file (UploadFile): The streaming multipart uploaded compressed binary wrapper file.

    Returns:
        ZipUploadResponse: Consolidated feedback data schema holding extraction paths and outcomes.
    """
    try:
        filename = file.filename or ""

        # Validation: Reject non-.zip structural input formats
        if not filename.lower().endswith(".zip"):
            return ZipUploadResponse(
                success=False,
                extract_path="",
                message="Only ZIP files are supported.",
            )

        # 1. Establish localized workspace directory transport segments
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        zip_file_path = os.path.join(upload_dir, filename)

        # 2. Chunk-wise copying using shutil to handle large zip files efficiently
        with open(zip_file_path, mode="wb") as target_buffer:
            shutil.copyfileobj(file.file, target_buffer)

        # 3. Build descriptive dynamic extraction directory namespaces
        base_name = os.path.splitext(filename)[0]
        extract_dir = os.path.join(upload_dir, base_name)
        os.makedirs(extract_dir, exist_ok=True)

        # 4. Invoke the native standard extraction platform sequence
        with zipfile.ZipFile(zip_file_path, mode="r") as zip_ref:
            zip_ref.extractall(extract_dir)

        absolute_extract_path = os.path.normpath(os.path.abspath(extract_dir))

        return ZipUploadResponse(
            success=True,
            extract_path=absolute_extract_path,
            message="ZIP uploaded and extracted successfully.",
        )

    except Exception as exc:
        logger.exception("ZIP archive transport and processing infrastructure caught an unexpected exception: %s", str(exc))
        return ZipUploadResponse(
            success=False,
            extract_path="",
            message="ZIP upload failed.",
        )


def generate_html_report(project_path: str) -> HtmlReportResponse:
    """Compile diagnostic density metrics into a structured human-readable HTML document.

    Invokes report generation systems, structures compiled metrics into clean tabular 
    representations, and renders the static report onto the local file system.

    Args:
        project_path (str): Path targeting dynamic project workspace directory structures.

    Returns:
        HtmlReportResponse: Consolidated data structure object holding written file routes.
    """
    try:
        # 1. Call the existing backend metrics calculation service
        report_data = generate_report(project_path)

        if not report_data.success:
            return HtmlReportResponse(
                success=False,
                file_path="",
                message="Failed to generate report.",
            )

        # 2. Initialize and assert target output storage parameters
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        html_file_path = os.path.join(report_dir, "report.html")

        # 3. Construct layout lines sequentially with basic tabular styling frameworks
        by_rule_rows = "".join(
            f"<tr><td style='border: 1px solid #ddd; padding: 8px;'>{rule}</td>"
            f"<td style='border: 1px solid #ddd; padding: 8px;'>{count}</td></tr>"
            for rule, count in report_data.by_rule.items()
        )

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI Code Auto Fixer Report</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; color: #333; line-height: 1.6;">
    <h1>AI Code Auto Fixer Report</h1>
    <hr style="border: 0; border-top: 1px solid #eee; margin-bottom: 30px;">
    
    <h2>Total Issues</h2>
    <p style="font-size: 24px; font-weight: bold; color: #d9534f; margin-top: 0;">{report_data.total_issues}</p>
    
    <h2>Issues by Tool</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-bottom: 30px;">
        <thead>
            <tr style="background-color: #f5f5f5; text-align: left;">
                <th style="border: 1px solid #ddd; padding: 8px;">Analyzer Tool</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Issues Found</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">Ruff</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{report_data.by_tool.ruff}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">Bandit</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{report_data.by_tool.bandit}</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 8px;">Semgrep</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{report_data.by_tool.semgrep}</td>
            </tr>
        </tbody>
    </table>
    
    <h2>Issues by Rule</h2>
    <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
        <thead>
            <tr style="background-color: #f5f5f5; text-align: left;">
                <th style="border: 1px solid #ddd; padding: 8px;">Rule Identifier</th>
                <th style="border: 1px solid #ddd; padding: 8px;">Occurrence Density</th>
            </tr>
        </thead>
        <tbody>
            {by_rule_rows if by_rule_rows else "<tr><td colspan='2' style='border: 1px solid #ddd; padding: 8px; text-align: center;'>No issues encountered.</td></tr>"}
        </tbody>
    </table>
</body>
</html>
"""

        # 4. Flush written structures onto the targeted path coordinates
        with open(html_file_path, mode="w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        absolute_html_path = os.path.normpath(os.path.abspath(html_file_path))

        return HtmlReportResponse(
            success=True,
            file_path=absolute_html_path,
            message="HTML report generated successfully.",
        )

    except Exception as exc:
        logger.exception("HTML visualization reporting subsystem encountered an unexpected execution failure: %s", str(exc))
        return HtmlReportResponse(
            success=False,
            file_path="",
            message="HTML report generation failed.",
        )


def rollback_git_backup(project_path: str, commit_hash: str) -> GitRollbackResponse:
    """Restore the project filesystem state to a specific revision via a hard Git reset.

    Asserts Git markers exist in the project scope environment and updates HEAD, 
    index, and working directories to point cleanly to the designated commit hash identifier.

    Args:
        project_path (str): Path targeting the local tracking Git workspace location.
        commit_hash (str): Alphanumeric cryptographic commit identifier token to restore.

    Returns:
        GitRollbackResponse: Consolidated execution data schema mapping rollback outcomes.
    """
    try:
        # Resolve and normalize targeting coordinates safely
        target_path = os.path.normpath(os.path.abspath(project_path))

        # Resolve parent tracking directory layer if targeting a specific file instance
        if os.path.isfile(target_path):
            repo_dir = os.path.dirname(target_path)
        else:
            repo_dir = target_path

        # Assert workspace directory layer validity constraints
        if not os.path.exists(repo_dir) or not os.path.isdir(repo_dir):
            return GitRollbackResponse(
                success=False,
                message="Project is not a Git repository.",
            )

        # Assert repository infrastructure marker presence mapping
        git_marker = os.path.join(repo_dir, ".git")
        if not os.path.exists(git_marker):
            return GitRollbackResponse(
                success=False,
                message="Project is not a Git repository.",
            )

        # Execute hard branch reset orchestration command
        result = subprocess.run(
            ["git", "reset", "--hard", commit_hash],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        # Return structured outcomes according to process exit codes
        if result.returncode == 0:
            return GitRollbackResponse(
                success=True,
                message="Rollback completed successfully.",
            )
        
        return GitRollbackResponse(
            success=False,
            message=result.stderr.strip(),
        )

    except Exception as exc:
        logger.exception("Git rollback orchestration subsystem caught an unexpected execution pipeline exception: %s", str(exc))
        return GitRollbackResponse(
            success=False,
            message="Git rollback failed.",
        )


def explain_issue(
    rule: str,
    message: str,
    file: str,
    line: int,
) -> ExplainResponse:
    """Resolve contextual analytical deep-dives and actionable remediation patterns for a rule.

    References an internal validation ledger of common diagnostic finding definitions, 
    matching rules to tailored explanations, compliance targets, and example fixes.

    Args:
        rule (str): The unique identification rule tag code to evaluate.
        message (str): The textual string diagnostic reported by the engine.
        file (str): Normalized structural path location of the targeted source module.
        line (int): The source code coordinate entry line number indicating violation site location.

    Returns:
        ExplainResponse: Contextual AI-driven explanation feedback data structure payload.
    """
    try:
        # Define the in-memory transitional definitions matrix mapping common rule logs
        rule_registry = {
            "B602": {
                "explanation": "The execution of subprocesses via shell wrapper layers exposes the application to severe shell injection vectors.",
                "recommendation": "Refactor execution commands to pass argument parameters as a structured collection sequence with shell execution disabled.",
                "example_fix": "import subprocess\nsubprocess.run(['ls', '-l'], check=True)"
            },
            "F401": {
                "explanation": "An imported module statement exists inside the document scope but is never referenced or used by any executable code blocks.",
                "recommendation": "Remove the unreferenced import instruction block safely to maintain codebase clarity and optimize compilation speeds.",
                "example_fix": "# Remove or delete the unused module line entirely"
            },
            "E501": {
                "explanation": "The target source code string length exceeds the threshold cap configuration limit for max characters per line.",
                "recommendation": "Deconstruct or divide elongated statement assignments across sequential lines using explicit brackets or continuation methods.",
                "example_fix": "long_string = (\n    'This is a broken statement divided across '\n    'multiple configuration segments for line length limits.'\n)"
            },
            "B101": {
                "explanation": "The usage of standard assert evaluation keywords is optimized out during compilation transitions under production optimization flags.",
                "recommendation": "Replace structural assertion guards with explicit control flow conditionals throwing standard exception errors.",
                "example_fix": "if not condition:\n    raise ValueError('Validation constraints failed')"
            }
        }

        if rule in rule_registry:
            match_data = rule_registry[rule]
            return ExplainResponse(
                success=True,
                rule=rule,
                explanation=match_data["explanation"],
                recommendation=match_data["recommendation"],
                example_fix=match_data["example_fix"],
            )

        return ExplainResponse(
            success=True,
            rule=rule,
            explanation="No detailed explanation is available for this rule.",
            recommendation="Refer to the analyzer documentation for more information.",
            example_fix="",
        )

    except Exception as exc:
        logger.exception("AI issue analysis framework encountered an unexpected pipeline exception for rule %s: %s", rule, str(exc))
        return ExplainResponse(
            success=False,
            rule=rule,
            explanation="",
            recommendation="",
            example_fix="",
        )


def get_issues_by_severity(project_path: str, severity: SeverityLevel) -> SeverityFilterResponse:
    """Scan a target workspace and isolate diagnostic findings matching a specific impact classification criteria.

    Leverages the core sequential scanning layer to aggregate deduplicated analysis logs,
    applies a structural static taxonomy to translate rule identifier codes into prioritization
    layers, and filters the results to match the requested severity criteria.

    Args:
        project_path (str): Path targeting directory structures or individual modules.
        severity (SeverityLevel): The impact classification prioritization filter requested.

    Returns:
        SeverityFilterResponse: Data framework package wrapping the filtered findings collections.
    """
    try:
        # 1. Reuse existing project core scan optimization pipeline layer
        scan_result = scan_project(project_path)

        if not scan_result.success:
            return SeverityFilterResponse(
                success=False,
                severity=severity,
                issues=[],
            )

        # 2. Establish deterministic prioritization rules layer mapping
        critical_rules = {"B602", "B607"}
        high_rules = {"B404", "B110"}
        medium_rules = {"E722"}

        filtered_list: List[SeverityIssue] = []

        # 3. Categorize and evaluate each generated rule violation footprint
        for issue in scan_result.issues:
            rule_tag = issue.rule

            if rule_tag in critical_rules:
                mapped_severity = SeverityLevel.CRITICAL
            elif rule_tag in high_rules:
                mapped_severity = SeverityLevel.HIGH
            elif rule_tag in medium_rules:
                mapped_severity = SeverityLevel.MEDIUM
            else:
                mapped_severity = SeverityLevel.LOW

            # 4. Filter only findings that align with requested impact criteria parameters
            if mapped_severity == severity:
                filtered_list.append(
                    SeverityIssue(
                        rule=issue.rule,
                        severity=mapped_severity,
                        message=issue.message,
                        file=issue.file,
                        line=issue.line,
                    )
                )

        return SeverityFilterResponse(
            success=True,
            severity=severity,
            issues=filtered_list,
        )

    except Exception as exc:
        logger.exception(
            "Impact severity classification and filtering system encountered an unhandled exception for severity %s: %s",
            severity,
            str(exc),
        )
        return SeverityFilterResponse(
            success=False,
            severity=severity,
            issues=[],
        )


def get_rule_information(rule_id: str) -> RuleSearchResponse:
    """Query the internal rule encyclopedia to fetch metadata profiles for a specific analyzer rule.

    References a deterministic in-memory dictionary lookup matrix to parse and return rule 
    summaries, security implications, and actionable structural optimization guidelines.

    Args:
        rule_id (str): The unique rule identification tag code to evaluate.

    Returns:
        RuleSearchResponse: Validation data package wrapping the rule descriptive profiles.
    """
    try:
        # 1. Establish the localized structural registry definitions matrix
        rule_database: Dict[str, Dict[str, str]] = {
            "B404": {
                "title": "Import of subprocess module detected",
                "description": "Indicates that the subprocess module is being imported. Subprocess calls can introduce severe security risks if untrusted input is passed incorrectly.",
                "recommendation": "Ensure all downstream execution parameters use discrete list arrays and keep shell execution completely disabled."
            },
            "B602": {
                "title": "Subprocess call with shell=True identified",
                "description": "Spawning execution sequences through shell translation wrappers exposes applications to dangerous command injection vectors.",
                "recommendation": "Refactor application code to pass execution arguments as a sequence list collection, completely ensuring shell=False remains active."
            },
            "B607": {
                "title": "Start process with a partial path string entry",
                "description": "Invoking operational systems executables using a relative path vector relies implicitly on shell search environments, exposing binaries to local spoofing vulnerabilities.",
                "recommendation": "Always declare the fully qualified absolute system route path coordinate string to target executable system binaries safely."
            },
            "B110": {
                "title": "Try-Except block with pass keyword pattern",
                "description": "Intercepting execution errors and silently discarding the tracking payload via pass constructs hides structural bug roots, making performance analysis complex.",
                "recommendation": "Incorporate structured logging frameworks inside evaluation blocks or catch highly specific transaction exceptions cleanly."
            },
            "E722": {
                "title": "Do not use bare except statements",
                "description": "Catching generic system anomalies via bare except statements blocks internal interrupts (like SystemExit or KeyboardInterrupt) and prevents clean worker exits.",
                "recommendation": "Refactor execution fallback loops to explicitly bind targets using 'except Exception:' or specify exact error definitions."
            }
        }

        # 2. Evaluate target registry presence constraints
        if rule_id in rule_database:
            metadata = rule_database[rule_id]
            return RuleSearchResponse(
                success=True,
                rule=rule_id,
                title=metadata["title"],
                description=metadata["description"],
                recommendation=metadata["recommendation"],
            )

        # 3. Handle gracefully when targeted keys are absent from our tracking matrix
        logger.info("Rule metadata lookup completed with no entries found for identifier: %s", rule_id)
        return RuleSearchResponse(
            success=False,
            rule=rule_id,
            title="Unknown Rule Identifier",
            description="The requested rule identifier does not match any known static analysis engine configuration records within our system database.",
            recommendation="Please review the validation string or consult the documentation of the specific backend analyzer engine tool.",
        )

    except Exception as exc:
        logger.exception(
            "Internal rule registry encyclopedia infrastructure encountered an unhandled exception for rule %s: %s",
            rule_id,
            str(exc),
        )
        return RuleSearchResponse(
            success=False,
            rule=rule_id,
            title="Error Querying Rule Database",
            description="An unhandled exception occurred while processing the requested rule identification lookup transaction.",
            recommendation="Retry the operation or look into backend operational traces for deeper structural analysis.",
        )