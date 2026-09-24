"""
AyuTrial-CTMS – FastAPI Application Entry Point
SIH Problem Statement ID: 26046
"""
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from app.core.config import get_settings
from app.core.database import engine, Base
from app.core.idempotency import IdempotencyConflictError
from app.models import clinical  # noqa: F401 – registers ORM models with Base
from app.routers.safety import router as safety_router
from app.routers.audit import router as audit_router
from app.routers.ecrf import router as ecrf_router
from app.routers.export import router as export_router
from app.routers.trials import router as trials_router
from app.routers.patients import router as patients_router
from app.routers.analytics import router as analytics_router
from app.routers.websockets import router as websockets_router
from app.routers.admin import router as admin_router
from app.routers.health import router as health_router
from app.routers.locks import router as locks_router
from app.routers.adherence import router as adherence_router
from app.routers.sync import router as sync_router

settings = get_settings()
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan – startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    log.info("AyuTrial-CTMS starting up …")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE trial_patients ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(100);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_trial_patients_telegram_chat_id ON trial_patients (telegram_chat_id);"))
    log.info("Database tables ensured.")
    yield
    await engine.dispose()
    log.info("AyuTrial-CTMS shut down.")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(safety_router)
    app.include_router(audit_router)
    app.include_router(ecrf_router)
    app.include_router(export_router)
    app.include_router(trials_router)
    app.include_router(patients_router)
    app.include_router(analytics_router)
    app.include_router(websockets_router)
    app.include_router(admin_router)
    app.include_router(health_router)
    app.include_router(locks_router)
    app.include_router(adherence_router)
    app.include_router(sync_router)

    @app.exception_handler(IdempotencyConflictError)
    async def idempotency_conflict_handler(request: Request, exc: IdempotencyConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "Duplicate transaction detected. Request with idempotency key already processed.",
                "idempotency_key": exc.idempotency_key,
            },
        )

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        return {"status": "ok", "service": settings.APP_TITLE, "version": settings.APP_VERSION}

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def root_dashboard():
        index_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        return HTMLResponse(content="<h1>AyuTrial-CTMS API</h1><p>Visit <a href='/docs'>/docs</a> for Swagger UI.</p>")

    return app


app = create_app()
