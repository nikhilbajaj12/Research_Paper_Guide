"""FastAPI application factory and startup."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .core import get_logger, settings, PaperGuideException
from .database import init_db, SessionLocal
from .utils.data_loader import load_initial_data
import traceback

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Conference-aware research paper submission assistant",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        debug=settings.DEBUG,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize database and other startup tasks."""
        logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
        logger.info(f"Environment: {settings.ENV}")
        logger.info(f"Debug mode: {settings.DEBUG}")

        # Initialize database
        init_db()
        logger.info("Database initialized")

        # Load initial data (conferences, guidelines)
        try:
            db = SessionLocal()
            stats = load_initial_data(db)
            logger.info(f"Initial data loaded: {stats}")
            db.close()
        except Exception as e:
            logger.error(f"Failed to load initial data: {str(e)}")

        # TODO: Initialize LLM clients if needed
        # TODO: Start background workers if needed

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        logger.info(f"Shutting down {settings.APP_NAME}")
        # TODO: Close database connections
        # TODO: Close LLM clients
        # TODO: Stop background workers

    # Global exception handler
    @app.exception_handler(PaperGuideException)
    async def paperguide_exception_handler(request, exc: PaperGuideException):
        """Handle PaperGuide-specific exceptions."""
        logger.error(f"PaperGuideException: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unexpected error: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )

    # Health check endpoint
    @app.get("/health", tags=["system"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "ok",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }

    # Root endpoint
    @app.get("/", tags=["system"])
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/api/docs",
        }

    # Include routes
    from .routes import conferences, papers, upload, compliance, packages, assistant, auto_fix
    app.include_router(conferences.router, tags=["conferences"])
    app.include_router(papers.router, tags=["papers"])
    app.include_router(upload.router, tags=["papers"])
    app.include_router(compliance.router, tags=["compliance"])
    app.include_router(packages.router, tags=["packages"])
    app.include_router(assistant.router, tags=["assistant"])
    app.include_router(auto_fix.router, tags=["auto-fix"])
    # from .routes import generation, projects
    # app.include_router(generation.router, prefix="/api/v1", tags=["generation"])
    # app.include_router(projects.router, prefix="/api/v1", tags=["projects"])

    return app


# Create the app
app = create_app()
