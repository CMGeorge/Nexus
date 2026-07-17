"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.auth.router import router as auth_router
from app.core.config import settings
from app.core.database import check_database_health
from app.core.middleware import RequestIDMiddleware, RequestTimingMiddleware
from app.core.redis_client import check_redis_health, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown lifecycle."""
    # Startup
    db_healthy = await check_database_health()
    if not db_healthy:
        print("WARNING: Database is not reachable")
    redis_healthy = await check_redis_health()
    if not redis_healthy:
        print("WARNING: Redis is not reachable — rate limiting and token blacklisting disabled")
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# ── Middleware ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestTimingMiddleware)


# ── Global exception handlers ──────────────────────────────────


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that returns RFC 7807 Problem Details."""
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": str(request.url),
        },
    )


# ── Routers ────────────────────────────────────────────────────
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])


# ── Health check ───────────────────────────────────────────────


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness/readiness endpoint."""
    db_healthy = await check_database_health()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "up" if db_healthy else "down",
    }
