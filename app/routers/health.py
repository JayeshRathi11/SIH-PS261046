from typing import Any
from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.watchdog import (
    get_unacknowledged_saes_diagnostics,
    get_watchdog_status,
)

router = APIRouter(prefix="/api/v1/health", tags=["System Health & Watchdog"])


@router.get(
    "/sae-daemon",
    summary="Dead-man's-switch health check for background SAE SLA countdown daemon",
)
async def check_sae_daemon_health(
    max_staleness: int = Query(30, description="Maximum allowable staleness in seconds"),
    db: AsyncSession = Depends(get_db),
) -> Response:
    status_data = get_watchdog_status(max_staleness_seconds=max_staleness)

    if status_data["is_healthy"]:
        return JSONResponse(status_code=status.HTTP_200_OK, content=status_data)

    diagnostics = await get_unacknowledged_saes_diagnostics(db)
    status_data["unacknowledged_saes_count"] = len(diagnostics)
    status_data["unacknowledged_saes"] = diagnostics

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=status_data,
    )
