import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import ClinicalTrial
from app.schemas.clinical import PortfolioKPIsOut
from app.services.analytics_service import get_portfolio_kpis
from app.services.spc_engine import analyze_trial_protocol_deviations

router = APIRouter(prefix="/api/v1/analytics", tags=["Executive Portfolio & DSMB Analytics"])


@router.get(
    "/portfolio-kpis",
    response_model=PortfolioKPIsOut,
    summary="Executive portfolio KPIs across trials, patient cohort, and pharmacovigilance safety",
)
async def get_portfolio_kpis_endpoint(
    force_refresh: bool = Query(False, description="Bypass in-memory cache and recompute from DB"),
    db: AsyncSession = Depends(get_db),
) -> PortfolioKPIsOut:
    kpis = await get_portfolio_kpis(db=db, force_refresh=force_refresh)
    return PortfolioKPIsOut(**kpis)


@router.get(
    "/protocol-deviations/{trial_id}",
    summary="Statistical Process Control (SPC) protocol deviations and drift anomalies",
)
async def get_protocol_deviations(
    trial_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    trial = await db.get(ClinicalTrial, trial_id)
    if trial is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClinicalTrial with id={trial_id} not found.",
        )
    return await analyze_trial_protocol_deviations(db, trial_id=trial_id)

