import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.tenant import get_tenant_context, TenantContext
from app.models.clinical import AccessAuditLog, TrialPatient, TrialSite
from app.schemas.clinical import (
    ConsentRevokeOut,
    TrialPatientCreate,
    TrialPatientOut,
    TrialSiteCreate,
    TrialSiteOut,
)
from app.services.patient_service import (
    enroll_patient,
    revoke_patient_consent,
    DuplicatePatientError,
    TrialNotRecruitingError,
)

router = APIRouter(prefix="/api/v1/patients", tags=["Patient Enrollment & DPDP Consent"])


@router.post(
    "/sites",
    response_model=TrialSiteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a participating trial site / hospital",
)
async def create_site(
    payload: TrialSiteCreate,
    db: AsyncSession = Depends(get_db),
) -> TrialSiteOut:
    site = TrialSite(
        site_code=payload.site_code,
        site_name=payload.site_name,
        city=payload.city,
        is_active=payload.is_active,
    )
    db.add(site)
    await db.commit()
    await db.refresh(site)
    return TrialSiteOut.model_validate(site)


@router.get(
    "/sites",
    response_model=List[TrialSiteOut],
    summary="List all trial sites",
)
async def list_sites(
    db: AsyncSession = Depends(get_db),
) -> List[TrialSiteOut]:
    stmt = select(TrialSite).order_by(TrialSite.site_code.asc())
    res = await db.execute(stmt)
    sites = res.scalars().all()
    return [TrialSiteOut.model_validate(s) for s in sites]


@router.post(
    "",
    response_model=TrialPatientOut,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll a patient into an active recruiting clinical trial",
)
async def create_patient(
    payload: TrialPatientCreate,
    db: AsyncSession = Depends(get_db),
) -> TrialPatientOut:
    try:
        patient = await enroll_patient(
            db,
            trial_id=payload.trial_id,
            usubjid=payload.usubjid,
            site_id=payload.site_id,
            prakriti_type=payload.prakriti_type,
            baseline_agni=payload.baseline_agni,
            consent_status=payload.consent_status,
        )
        return TrialPatientOut.model_validate(patient)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except TrialNotRecruitingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except DuplicatePatientError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.get(
    "",
    response_model=List[TrialPatientOut],
    summary="List patients filtered by tenant site or global access",
)
async def list_patients(
    trial_id: Optional[uuid.UUID] = Query(None),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> List[TrialPatientOut]:
    stmt = select(TrialPatient)
    if trial_id:
        stmt = stmt.where(TrialPatient.trial_id == trial_id)
    if not tenant.has_global_access and tenant.site_id is not None:
        stmt = stmt.where(TrialPatient.site_id == tenant.site_id)
    stmt = stmt.order_by(TrialPatient.enrolled_at.asc())
    res = await db.execute(stmt)
    patients = res.scalars().all()
    return [TrialPatientOut.model_validate(p) for p in patients]


@router.post(
    "/{patient_id}/consent/revoke",
    response_model=ConsentRevokeOut,
    summary="Revoke consent under DPDP Act 2023",
)
async def revoke_consent(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConsentRevokeOut:
    try:
        patient = await revoke_patient_consent(db, patient_id=patient_id)
        return ConsentRevokeOut(
            patient_id=patient.id,
            usubjid=patient.usubjid,
            consent_status=patient.consent_status,
            revoked_at=datetime.now(tz=timezone.utc),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/{patient_id}/dpdp-purge",
    summary="Execute DPDP Act 2023 Cryptographic Purge & Pseudonymization Cascade",
)
async def dpdp_purge_patient(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    try:
        from app.services.dpdp_purge_cascade import execute_dpdp_purge_cascade
        result = await execute_dpdp_purge_cascade(patient_id, db)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc



@router.get(
    "/{patient_id}",
    response_model=TrialPatientOut,
    summary="Get patient details by ID with tenant isolation & DPDP read logging",
)
async def get_patient(
    patient_id: uuid.UUID,
    request: Request,
    purpose_code: str = Query("PURPOSE_CLINICAL_REVIEW"),
    tenant: TenantContext = Depends(get_tenant_context),
    db: AsyncSession = Depends(get_db),
) -> TrialPatientOut:
    stmt = select(TrialPatient).where(TrialPatient.id == patient_id)
    res = await db.execute(stmt)
    patient = res.scalar_one_or_none()
    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TrialPatient with id={patient_id} not found.",
        )

    if not tenant.has_global_access and patient.site_id is not None and tenant.site_id != patient.site_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Subject belongs to another trial site.",
        )

    client_ip = request.client.host if request and request.client else None
    log_entry = AccessAuditLog(
        user_id=tenant.user_id,
        patient_id=patient.id,
        purpose_code=purpose_code,
        ip_address=client_ip,
    )
    db.add(log_entry)
    await db.commit()

    return TrialPatientOut.model_validate(patient)
