"""
FastAPI Main Application

Entry point for the Film Financing Navigator API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.

    Handles:
    - Database connection pool initialization
    - Redis connection
    - Celery worker health check
    - Policy data caching
    """
    # Startup
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 API Prefix: {settings.API_V1_PREFIX}")

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Warm up policy cache (load all policies into Redis)

    yield

    # Shutdown
    print("👋 Shutting down application")
    # TODO: Close database connections
    # TODO: Close Redis connections


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Trusted Host Middleware (production security)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["api.filmfinance.com", "*.filmfinance.com"]
    )


# Root endpoint
@app.get("/", tags=["Health"])
async def root():
    """API root endpoint with service information."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "environment": settings.ENVIRONMENT
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for load balancers and monitoring.

    Returns:
        Service health status with component checks
    """
    # TODO: Add database ping
    # TODO: Add Redis ping
    # TODO: Add Celery worker check

    return {
        "status": "healthy",
        "checks": {
            "database": "ok",  # TODO: actual check
            "redis": "ok",     # TODO: actual check
            "celery": "ok"     # TODO: actual check
        }
    }


# API v1 Router
from app.api.v1.api import api_router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.

    Logs error to Sentry in production, returns generic message to client.
    """
    # TODO: Log to Sentry if configured

    if settings.ENVIRONMENT == "development":
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": str(exc),
                    "type": type(exc).__name__
                }
            }
        )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
