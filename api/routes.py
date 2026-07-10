import json
import os
from fastapi import APIRouter, UploadFile, File
from api.models import (
    ScanRequest,
    ScanResponse,
    FixRequest,
    FixResponse,
    ReportResponse,
    JobResponse,
    JobStatus,
    ExportResponse,
    ExportFormat,
    ScanHistoryResponse,
    SupportedToolsResponse,
    ConfigResponse,
    FixPreviewResponse,
    DiffResponse,
    GitBackupResponse,
    ZipUploadResponse,
    HtmlReportResponse,
    GitRollbackRequest,
    GitRollbackResponse,
    ExplainRequest,
    ExplainResponse,
    SeverityLevel,
    SeverityFilterResponse,
    RuleSearchResponse,
    DashboardResponse,
    DashboardSummary,
)
from api.services import (
    scan_project,
    fix_project,
    generate_report,
    start_fix_job,
    get_job,
    export_report,
    get_scan_history,
    get_supported_tools,
    get_config,
    preview_fixes,
    generate_diff,
    create_git_backup,
    upload_zip,
    generate_html_report,
    rollback_git_backup,
    explain_issue,
    get_issues_by_severity,
    get_rule_information,
    get_dashboard,
)

# Initialize the central API router context
router = APIRouter()

@router.get("/", response_model=dict[str, str])
async def get_root() -> dict[str, str]:
    """Retrieve the base welcome payload for the AI Code Auto Fixer API."""
    return {"message": "AI Code Auto Fixer API"}

@router.get("/health", response_model=dict[str, str])
async def get_health() -> dict[str, str]:
    """Execute a basic shallow health-check diagnostic verification."""
    return {"status": "ok"}

@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest) -> ScanResponse:
    """Scan an absolute file-system path structure using enabled static analysis engines."""
    return scan_project(request.project_path)

@router.post("/fix", response_model=FixResponse)
async def fix(request: FixRequest) -> FixResponse:
    """Remediate static analysis engine violations found within a file-system path."""
    return fix_project(request.project_path)

@router.get("/report")
async def get_report(project_path: str = "."):
    """Safely fetch existing static reports without re-triggering expensive scanning cycles."""
    report_file = os.path.join(project_path, ".agent_report.json")
    
    if os.path.exists(report_file):
        with open(report_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                pass

    return {
        "success": True, 
        "data": {
            "total_files": 0, 
            "total_issues": 0, 
            "engine_findings": {"bandit": 0, "ruff": 0, "semgrep": 0}
        }
    }

@router.post("/jobs/fix", response_model=JobResponse)
async def create_fix_job(request: FixRequest) -> JobResponse:
    """Initialize and dispatch a non-blocking background task to handle project automated corrections."""
    return start_fix_job(request.project_path)

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def job_status(job_id: str) -> JobResponse:
    """Fetch the active execution status lifecycle frame of an asynchronous background job."""
    job = get_job(job_id)
    if job is None:
        return JobResponse(
            job_id=job_id,
            status=JobStatus.FAILED,
            message="Job not found."
        )
    return job

@router.get("/report/export", response_model=ExportResponse)
async def export(
    project_path: str,
    export_format: ExportFormat,
) -> ExportResponse:
    """Generate diagnostic density metrics and serialize findings payload tracking reports to disk."""
    return export_report(project_path, export_format)

@router.get("/history", response_model=ScanHistoryResponse)
async def history() -> ScanHistoryResponse:
    """Fetch the compiled in-memory ledger timeline archiving previous diagnostic scan operations."""
    return get_scan_history()

@router.get("/tools", response_model=SupportedToolsResponse)
async def tools() -> SupportedToolsResponse:
    """Fetch structured operational information tracking active and available backend engine subsystems."""
    return get_supported_tools()

@router.get("/config", response_model=ConfigResponse)
async def config() -> ConfigResponse:
    """Fetch active operational threshold parameters detailing global system runtime setting frames."""
    return get_config()

@router.post("/preview", response_model=FixPreviewResponse)
async def preview(request: FixRequest) -> FixPreviewResponse:
    """Generate a non-destructive preview summarizing proposed automated source-code modifications."""
    return preview_fixes(request.project_path)

@router.post("/diff", response_model=DiffResponse)
async def diff(request: FixRequest) -> DiffResponse:
    """Generate line-by-line file modification differentials tracking prospective source adjustments."""
    return generate_diff(request.project_path)

@router.post("/git/backup", response_model=GitBackupResponse)
async def git_backup(request: FixRequest) -> GitBackupResponse:
    """Commit active repository alterations to create a transactional rollback node prior to code remediation."""
    return create_git_backup(request.project_path)

@router.post("/upload/zip", response_model=ZipUploadResponse)
async def upload_project_zip(
    file: UploadFile = File(...)
) -> ZipUploadResponse:
    """Receive, store, and unpack a compressed multipart file archive containing python source projects."""
    return upload_zip(file)

@router.get("/report/html", response_model=HtmlReportResponse)
async def html_report(project_path: str) -> HtmlReportResponse:
    """Analyze a targeted workspace to compute and serialize visual web tracking layouts to disk."""
    return generate_html_report(project_path)

@router.post("/git/rollback", response_model=GitRollbackResponse)
async def git_rollback(request: GitRollbackRequest) -> GitRollbackResponse:
    """Restore the project file-system environment status backward to a designated cryptographic commit node."""
    return rollback_git_backup(request.project_path, request.commit_hash)

@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest) -> ExplainResponse:
    """Generate AI-powered issue explanations, remediation strategies, and compliant fix examples."""
    return explain_issue(request.rule, request.message, request.file, request.line)

@router.get("/issues/severity", response_model=SeverityFilterResponse)
async def issues_by_severity(
    project_path: str,
    severity: SeverityLevel,
) -> SeverityFilterResponse:
    """Scan a target workspace path context and retrieve a filtered subset collection matching a designated severity level."""
    return get_issues_by_severity(project_path, severity)

@router.get("/issues", response_model=SeverityFilterResponse)
async def get_issues(
    project_path: str,
    severity: SeverityLevel,
) -> SeverityFilterResponse:
    """Retrieve deduplicated engine findings from a project path filtered explicitly by impact severity level."""
    return get_issues_by_severity(project_path, severity)

@router.get("/rules/{rule_id}", response_model=RuleSearchResponse)
async def get_rule(rule_id: str) -> RuleSearchResponse:
    """Query the internal rules engine metadata database to retrieve descriptive profiles for an explicit static finding code."""
    return get_rule_information(rule_id)

@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(project_path: str = ".") -> DashboardResponse:
    """Fetch dashboard metrics from the latest generated scan report."""

    project_path = os.path.abspath(project_path)

    report_file = os.path.join(
        project_path,
        ".agent_report.json",
    )

    history_response = get_scan_history()

    scans_list = []

    if hasattr(history_response, "scans"):
        scans_list = history_response.scans

    elif hasattr(history_response, "data"):
        scans_list = history_response.data

    elif isinstance(history_response, list):
        scans_list = history_response

    report = {}

    if os.path.exists(report_file):
        try:
            with open(
                report_file,
                "r",
                encoding="utf-8",
            ) as fp:
                report = json.load(fp)

        except Exception:
          report = {}

    total_issues = report.get("total_issues", 0)

    by_tool = report.get(
        "by_tool",
        {
            "ruff": 0,
            "bandit": 0,
            "semgrep": 0,
        },
    )

    issues = report.get("issues", [])

    total_files = len(
        {
            issue.get("file", "")
            for issue in issues
            if issue.get("file")
        }
    )
    security_score = "A+"

    if total_issues > 0:
        security_score = "C"

    if total_issues > 10:
        security_score = "D"

    if total_issues > 25:
        security_score = "F"

    summary = DashboardSummary(
        total_scans=total_files,
        total_issues=total_issues,
        total_fixed=0,
    )

    return DashboardResponse(
        success=True,

        summary=summary,

        top_rules={
            "ruff": by_tool.get("ruff", 0),
            "bandit": by_tool.get("bandit", 0),
            "semgrep": by_tool.get("semgrep", 0),
        },

        recent_scans=scans_list,
    )