"""
AyuTrial-CTMS – Safety Router
POST /api/v1/safety/adverse-event
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.clinical import AdverseEventCreate, AdverseEventOut
from app.services.safety import create_adverse_event

router = APIRouter(prefix="/api/v1/safety", tags=["Safety & Pharmacovigilance"])


@router.post(
    "/adverse-event",
    response_model=AdverseEventOut,
    status_code=status.HTTP_201_CREATED,
    summary="Log an adverse event (SAE auto-trigger enabled)",
    description=(
        "Records an adverse event for a trial patient. "
        "If severity is HOSPITALIZATION, LIFE_THREATENING, or DEATH, "
        "the SAE flag is automatically set and a 24-hour SLA deadline "
        "is computed per NDCT Rules 2019. "
        "Row-level pessimistic locking prevents concurrent writes for the same patient."
    ),
)
async def log_adverse_event(
    payload: AdverseEventCreate,
    db: AsyncSession = Depends(get_db),
) -> AdverseEventOut:
    try:
        ae = await create_adverse_event(
            db,
            patient_id=payload.patient_id,
            severity=payload.severity,
            clinical_notes=payload.clinical_notes,
            reported_by=payload.reported_by,
        )
        return AdverseEventOut.model_validate(ae)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log adverse event: {exc}",
        ) from exc
