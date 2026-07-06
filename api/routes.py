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
    """Retrieve the base welcome payload for the AI Code Auto Fixer API.

    Returns:
        dict[str, str]: A dictionary containing the API description message.
    """
    return {"message": "AI Code Auto Fixer API"}


@router.get("/health", response_model=dict[str, str])
async def get_health() -> dict[str, str]:
    """Execute a basic shallow health-check diagnostic verification.

    Returns:
        dict[str, str]: A dictionary containing the operational status indicator.
    """
    return {"status": "ok"}


@router.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest) -> ScanResponse:
    """Scan an absolute file-system path structure using enabled static analysis engines.

    Args:
        request (ScanRequest): Input structural target path wrapper container payload.

    Returns:
        ScanResponse: Compiled structural report listing rule findings.
    """
    return scan_project(request.project_path)


@router.post("/fix", response_model=FixResponse)
async def fix(request: FixRequest) -> FixResponse:
    """Remediate static analysis engine violations found within a file-system path.

    Args:
        request (FixRequest): Input structural target path wrapper container payload.

    Returns:
        FixResponse: Compiled structural report summarizing applied automation statistics.
    """
    return fix_project(request.project_path)


@router.get("/report", response_model=ReportResponse)
async def report(project_path: str) -> ReportResponse:
    """Analyze a targeted workspace to compute and compile density metric analytical reports.

    Args:
        project_path (str): The local filesystem query string location to be evaluated.

    Returns:
        ReportResponse: Consolidated analytics overview breaking down rules and tools usage.
    """
    return generate_report(project_path)


@router.post("/jobs/fix", response_model=JobResponse)
async def create_fix_job(request: FixRequest) -> JobResponse:
    """Initialize and dispatch a non-blocking background task to handle project automated corrections.

    Args:
        request (FixRequest): Input structural target path wrapper container payload.

    Returns:
        JobResponse: Initial tracking container payload documenting the newly queued task status.
    """
    return start_fix_job(request.project_path)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def job_status(job_id: str) -> JobResponse:
    """Fetch the active execution status lifecycle frame of an asynchronous background job.

    Args:
        job_id (str): The unique string identifier assigned to the target worker task.

    Returns:
        JobResponse: Current execution tracking context payload snapshot of the requested job.
    """
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
    """Generate diagnostic density metrics and serialize findings payload tracking reports to disk.

    Args:
        project_path (str): The target filesystem directory coordinate routing string to evaluate.
        export_format (ExportFormat): The selected structural mapping encoding standard (json or csv).

    Returns:
        ExportResponse: Execution feedback metadata confirming written download target paths.
    """
    return export_report(project_path, export_format)


@router.get("/history", response_model=ScanHistoryResponse)
async def history() -> ScanHistoryResponse:
    """Fetch the compiled in-memory ledger timeline archiving previous diagnostic scan operations.

    Returns:
        ScanHistoryResponse: Structured aggregate payload wrapping sequential execution records.
    """
    return get_scan_history()


@router.get("/tools", response_model=SupportedToolsResponse)
async def tools() -> SupportedToolsResponse:
    """Fetch structured operational information tracking active and available backend engine subsystems.

    Returns:
        SupportedToolsResponse: Consolidated ledger payload detailing active static analysis frameworks.
    """
    return get_supported_tools()


@router.get("/config", response_model=ConfigResponse)
async def config() -> ConfigResponse:
    """Fetch active operational threshold parameters detailing global system runtime setting frames.

    Returns:
        ConfigResponse: Unified serialization blueprint capturing running pipeline environments.
    """
    return get_config()


@router.post("/preview", response_model=FixPreviewResponse)
async def preview(request: FixRequest) -> FixPreviewResponse:
    """Generate a non-destructive preview summarizing proposed automated source-code modifications.

    Args:
        request (FixRequest): Input structural target path wrapper container payload.

    Returns:
        FixPreviewResponse: Structured payload listing prospective automated remediation previews.
    """
    return preview_fixes(request.project_path)


@router.post("/diff", response_model=DiffResponse)
async def diff(request: FixRequest) -> DiffResponse:
    """Generate line-by-line file modification differentials tracking prospective source adjustments.

    Args:
        request (FixRequest): Input structural target path wrapper container payload.

    Returns:
        DiffResponse: Consolidated sequential bundle tracking isolated text line substitutions.
    """
    return generate_diff(request.project_path)


@router.post("/git/backup", response_model=GitBackupResponse)
async def git_backup(request: FixRequest) -> GitBackupResponse:
    """Commit active repository alterations to create a transactional rollback node prior to code remediation.

    Args:
        request (FixRequest): Input structural target path wrapper container payload.

    Returns:
        GitBackupResponse: Execution context summary capturing the tracking result state and backup commit identifier.
    """
    return create_git_backup(request.project_path)


@router.post("/upload/zip", response_model=ZipUploadResponse)
async def upload_project_zip(
    file: UploadFile = File(...)
) -> ZipUploadResponse:
    """Receive, store, and unpack a compressed multipart file archive containing python source projects.

    Args:
        file (UploadFile): Stream payload containing the incoming binary compressed attachment structure.

    Returns:
        ZipUploadResponse: Consolidated feedback data schema holding target extraction paths and outcomes.
    """
    return upload_zip(file)


@router.get("/report/html", response_model=HtmlReportResponse)
async def html_report(project_path: str) -> HtmlReportResponse:
    """Analyze a targeted workspace to compute and serialize visual web tracking layouts to disk.

    Args:
        project_path (str): The local filesystem query string location to be evaluated.

    Returns:
        HtmlReportResponse: Execution feedback metadata pointing to written web visualization layouts.
    """
    return generate_html_report(project_path)


@router.post("/git/rollback", response_model=GitRollbackResponse)
async def git_rollback(request: GitRollbackRequest) -> GitRollbackResponse:
    """Restore the project file-system environment status backward to a designated cryptographic commit node.

    Args:
        request (GitRollbackRequest): Input context schema defining target repository routes and target commit hash tokens.

    Returns:
        GitRollbackResponse: Execution feedback metadata recording structural transformation operation outcomes.
    """
    return rollback_git_backup(
        request.project_path,
        request.commit_hash,
    )


@router.post("/explain", response_model=ExplainResponse)
async def explain(request: ExplainRequest) -> ExplainResponse:
    """Generate AI-powered issue explanations, remediation strategies, and compliant fix examples.

    Args:
        request (ExplainRequest): Input target containing the static rule, diagnostic message, and file line details.

    Returns:
        ExplainResponse: Contextual analysis response holding explanation logs and demonstration patches.
    """
    return explain_issue(
        request.rule,
        request.message,
        request.file,
        request.line,
    )


@router.get("/issues/severity", response_model=SeverityFilterResponse)
async def issues_by_severity(
    project_path: str,
    severity: SeverityLevel,
) -> SeverityFilterResponse:
    """Scan a target workspace path context and retrieve a filtered subset collection matching a designated severity level.

    Args:
        project_path (str): The target filesystem directory or file route string location to evaluate.
        severity (SeverityLevel): The exact target impact metric used to isolate specific findings entries.

    Returns:
        SeverityFilterResponse: Filtered findings response container satisfying matching priority rules.
    """
    return get_issues_by_severity(project_path, severity)


@router.get("/issues", response_model=SeverityFilterResponse)
async def get_issues(
    project_path: str,
    severity: SeverityLevel,
) -> SeverityFilterResponse:
    """Retrieve deduplicated engine findings from a project path filtered explicitly by impact severity level.

    Args:
        project_path (str): The local absolute or relative filesystem route tracking the target code base to evaluate.
        severity (SeverityLevel): The target categorical priority impact threshold tier chosen for filtering the results.

    Returns:
        SeverityFilterResponse: Consolidated data frame listing only analysis issues matching the given criteria.
    """
    return get_issues_by_severity(project_path, severity)


@router.get("/rules/{rule_id}", response_model=RuleSearchResponse)
async def get_rule(rule_id: str) -> RuleSearchResponse:
    """Query the internal rules engine metadata database to retrieve descriptive profiles for an explicit static finding code.

    Args:
        rule_id (str): The explicit rule designation key code string identifier to evaluate.

    Returns:
        RuleSearchResponse: Metadata profile packaging titles, context definitions, and compliant code resolutions.
    """
    return get_rule_information(rule_id)


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard() -> DashboardResponse:
    """Fetch the high-level analytical dashboard aggregating ecosystem operation statistics.

    Returns:
        DashboardResponse: Core metrics payload visual summary snapshot tracking remediation platform health.
    """
    return get_dashboard()