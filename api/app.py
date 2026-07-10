"""Main FastAPI application initialization and routing assembly.

Configures application metadata, operational limits, and includes all sub-routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router


def create_app() -> FastAPI:
    """Initialize and configure the central FastAPI application instance.

    Returns:
        FastAPI: Fully configured FastAPI application instance.
    """
    app = FastAPI(
        title="AI Code Auto Fixer",
        description="REST API for the AI Code Auto Fixer pipeline",
        version="1.0.0",
    )

    # Configure CORS middleware safely for local development variations
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",   # Vite dev server standard header
            "http://127.0.0.1:5173",   # Vite dev server loopback IP header fallback
            "http://localhost:5173/",  # Standard trailing slash edge cases
            "http://127.0.0.1:5173/"
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],          # Explicitly bubble up runtime headers to browser
    )

    # Attach the assembled API routing vectors
    app.include_router(api_router)

    return app


# Root application instance for ASGI server execution target
app = create_app()