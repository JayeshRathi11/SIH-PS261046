import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import AuditAction, ConsentStatus, ECRFRecord, TrialPatient
from app.schemas.clinical import ECRFRecordCreate, ECRFRecordOut
from app.services.audit import append_audit_entry

router = APIRouter(prefix="/api/v1/patients", tags=["eCRF Clinical Data"])


@router.post(
    "/{patient_id}/ecrf",
    response_model=ECRFRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record eCRF data for patient visit",
)
async def submit_ecrf(
    patient_id: uuid.UUID,
    payload: ECRFRecordCreate,
    db: AsyncSession = Depends(get_db),
) -> ECRFRecordOut:
    stmt = select(TrialPatient).where(TrialPatient.id == patient_id).with_for_update()
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TrialPatient with id={patient_id} not found.",
        )

    if patient.consent_status == ConsentStatus.WITHDRAWN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject has withdrawn consent under DPDP Act",
        )

    check_dup_stmt = select(ECRFRecord).where(
        ECRFRecord.patient_id == patient_id,
        ECRFRecord.visit_number == payload.visit_number,
    )
    dup_res = await db.execute(check_dup_stmt)
    existing_record = dup_res.scalar_one_or_none()
    if existing_record is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"eCRF record for visit {payload.visit_number} already exists for this patient.",
        )

    ecrf = ECRFRecord(
        patient_id=patient.id,
        trial_id=patient.trial_id,
        visit_number=payload.visit_number,
        visit_name=payload.visit_name,
        form_data=payload.form_data,
    )
    db.add(ecrf)
    await db.flush()

    field_changes = {
        "patient_id": str(patient.id),
        "trial_id": str(patient.trial_id),
        "visit_number": payload.visit_number,
        "visit_name": payload.visit_name,
        "form_data": payload.form_data,
    }
    await append_audit_entry(
        db,
        entity_name="ecrf_records",
        entity_id=str(ecrf.id),
        action_type=AuditAction.INSERT,
        field_changes=field_changes,
        modified_by=payload.modified_by,
    )

    await db.commit()
    await db.refresh(ecrf)
    return ECRFRecordOut.model_validate(ecrf)


@router.get(
    "/{patient_id}/ecrf",
    response_model=List[ECRFRecordOut],
    summary="Get all eCRF records for patient",
)
async def get_patient_ecrfs(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[ECRFRecordOut]:
    stmt = (
        select(ECRFRecord)
        .where(ECRFRecord.patient_id == patient_id)
        .order_by(ECRFRecord.visit_number.asc())
    )
    result = await db.execute(stmt)
    records = result.scalars().all()
    return [ECRFRecordOut.model_validate(r) for r in records]
