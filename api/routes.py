"""API Route definitions and endpoint handlers using FastAPI APIRouter.

Defines base routing structures, health-check diagnostics, and project analysis entry vectors.
"""

from fastapi import APIRouter
from api.models import ScanRequest, ScanResponse, FixRequest, FixResponse
from api.services import scan_project, fix_project

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