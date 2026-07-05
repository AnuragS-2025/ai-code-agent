"""API Route definitions and endpoint handlers using FastAPI APIRouter.

Defines base routing structures and health-check diagnostics.
"""

from fastapi import APIRouter

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