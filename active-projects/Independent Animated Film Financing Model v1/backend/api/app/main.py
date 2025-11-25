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

    # Initialize database
    try:
        from app.db.session import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database initialization skipped: {e}")

    # TODO: Initialize Redis connection
    # TODO: Warm up policy cache (load all policies into Redis)

    yield

    # Shutdown
    print("👋 Shutting down application")
    # Database connections are automatically closed by SQLAlchemy


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
    from datetime import datetime
    import time

    checks = {}
    overall_status = "healthy"
    start_time = time.time()

    # Database check
    try:
        from app.db.session import test_connection
        db_ok = test_connection()
        checks["database"] = "ok" if db_ok else "degraded"
        if not db_ok:
            overall_status = "degraded"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:50]}"
        overall_status = "unhealthy"

    # Policy Registry check (Engine 1 core service)
    try:
        from app.core.path_setup import BACKEND_ROOT
        from engines.incentive_calculator.policy_loader import PolicyLoader
        policies_dir = BACKEND_ROOT / "data" / "policies"
        loader = PolicyLoader(policies_dir)
        policy_ids = loader.get_policy_ids()
        checks["policy_registry"] = f"ok ({len(policy_ids)} policies)"
    except Exception as e:
        checks["policy_registry"] = f"error: {str(e)[:50]}"
        overall_status = "degraded"

    # Capital Program Manager check (Engine 5)
    try:
        from engines.capital_programs import CapitalProgramManager
        # Just verify import works - manager is stateless
        checks["capital_program_manager"] = "ok"
    except Exception as e:
        checks["capital_program_manager"] = f"error: {str(e)[:50]}"

    # Calculate response time
    response_time_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "response_time_ms": response_time_ms,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": checks
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
