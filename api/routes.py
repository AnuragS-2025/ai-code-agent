"""API Route definitions and endpoint handlers using FastAPI APIRouter.

Defines base routing structures, health-check diagnostics, and project analysis entry vectors.
"""

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