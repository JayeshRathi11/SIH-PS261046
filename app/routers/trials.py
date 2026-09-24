import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import AuditAction, ClinicalTrial, TrialStatus
from app.schemas.clinical import AdvanceStatusPayload, ClinicalTrialCreate, ClinicalTrialOut
from app.services.audit import append_audit_entry
from app.services.trial_lifecycle import (
    advance_trial_status,
    InvalidCtriError,
    InvalidTransitionError,
    MissingIecError,
)

router = APIRouter(prefix="/api/v1/trials", tags=["CTRI Protocols & Trials"])


@router.post(
    "",
    response_model=ClinicalTrialOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a prospective clinical trial protocol",
)
async def create_trial(
    payload: ClinicalTrialCreate,
    db: AsyncSession = Depends(get_db),
) -> ClinicalTrialOut:
    existing_stmt = select(ClinicalTrial).where(ClinicalTrial.protocol_id == payload.protocol_id)
    existing_res = await db.execute(existing_stmt)
    if existing_res.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Trial with protocol_id '{payload.protocol_id}' already exists.",
        )

    trial = ClinicalTrial(
        protocol_id=payload.protocol_id,
        study_title=payload.study_title,
        iec_clearance_number=payload.iec_clearance_number,
        ctri_registration_id=payload.ctri_registration_id,
        status=TrialStatus.DRAFT,
    )
    db.add(trial)
    await db.flush()

    await append_audit_entry(
        db,
        entity_name="clinical_trials",
        entity_id=str(trial.id),
        action_type=AuditAction.INSERT,
        field_changes={
            "protocol_id": trial.protocol_id,
            "study_title": trial.study_title,
            "status": TrialStatus.DRAFT.value,
        },
        modified_by="protocol_admin",
    )
    await db.commit()
    await db.refresh(trial)
    return ClinicalTrialOut.model_validate(trial)


@router.put(
    "/{trial_id}/advance-status",
    response_model=ClinicalTrialOut,
    summary="Advance prospective trial protocol lifecycle",
)
@router.post(
    "/{trial_id}/advance-status",
    response_model=ClinicalTrialOut,
    summary="Advance prospective trial protocol lifecycle (POST alias)",
)
async def transition_trial_status(
    trial_id: uuid.UUID,
    payload: AdvanceStatusPayload,
    db: AsyncSession = Depends(get_db),
) -> ClinicalTrialOut:
    try:
        trial = await advance_trial_status(
            db,
            trial_id=trial_id,
            target_status=payload.target_status,
            iec_clearance_number=payload.iec_clearance_number,
            ctri_registration_id=payload.ctri_registration_id,
            modified_by=payload.modified_by,
        )
        return ClinicalTrialOut.model_validate(trial)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except MissingIecError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvalidCtriError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/{trial_id}",
    response_model=ClinicalTrialOut,
    summary="Get trial details by ID",
)
async def get_trial(
    trial_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ClinicalTrialOut:
    stmt = select(ClinicalTrial).where(ClinicalTrial.id == trial_id)
    res = await db.execute(stmt)
    trial = res.scalar_one_or_none()
    if trial is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ClinicalTrial with id={trial_id} not found.",
        )
    return ClinicalTrialOut.model_validate(trial)


@router.get(
    "",
    response_model=List[ClinicalTrialOut],
    summary="List all clinical trials",
)
async def list_trials(
    db: AsyncSession = Depends(get_db),
) -> List[ClinicalTrialOut]:
    stmt = select(ClinicalTrial).order_by(ClinicalTrial.created_at.desc())
    res = await db.execute(stmt)
    trials = res.scalars().all()
    return [ClinicalTrialOut.model_validate(t) for t in trials]
