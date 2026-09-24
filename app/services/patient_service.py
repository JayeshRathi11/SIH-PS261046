import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AuditAction, ClinicalTrial, ConsentStatus, TrialPatient, TrialStatus
from app.services.audit import append_audit_entry


class TrialNotRecruitingError(Exception):
    pass


class DuplicatePatientError(Exception):
    pass


async def enroll_patient(
    db: AsyncSession,
    *,
    trial_id: uuid.UUID,
    usubjid: str,
    site_id: Optional[uuid.UUID] = None,
    prakriti_type: Optional[str] = None,
    baseline_agni: Optional[str] = None,
    consent_status: ConsentStatus = ConsentStatus.OBTAINED,
    modified_by: str = "investigator",
) -> TrialPatient:
    stmt = select(ClinicalTrial).where(ClinicalTrial.id == trial_id)
    res = await db.execute(stmt)
    trial = res.scalar_one_or_none()
    if trial is None:
        raise ValueError(f"ClinicalTrial with id={trial_id} not found.")

    if trial.status != TrialStatus.RECRUITING:
        raise TrialNotRecruitingError(
            f"Trial is not active for enrollment. Current status: '{trial.status.value}' (must be 'RECRUITING')."
        )

    dup_stmt = select(TrialPatient).where(
        TrialPatient.trial_id == trial_id,
        TrialPatient.usubjid == usubjid,
    )
    dup_res = await db.execute(dup_stmt)
    if dup_res.scalar_one_or_none() is not None:
        raise DuplicatePatientError(f"Patient with usubjid '{usubjid}' already enrolled in this trial.")

    patient = TrialPatient(
        trial_id=trial_id,
        usubjid=usubjid,
        site_id=site_id,
        prakriti_type=prakriti_type,
        baseline_agni=baseline_agni,
        consent_status=consent_status,
    )
    db.add(patient)
    await db.flush()

    field_changes = {
        "trial_id": str(trial_id),
        "usubjid": usubjid,
        "site_id": str(site_id) if site_id else None,
        "prakriti_type": prakriti_type,
        "baseline_agni": baseline_agni,
        "consent_status": consent_status.value,
    }
    await append_audit_entry(
        db,
        entity_name="trial_patients",
        entity_id=str(patient.id),
        action_type=AuditAction.INSERT,
        field_changes=field_changes,
        modified_by=modified_by,
    )

    await db.commit()
    await db.refresh(patient)
    return patient


async def revoke_patient_consent(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    modified_by: str = "subject",
) -> TrialPatient:
    stmt = (
        select(TrialPatient)
        .where(TrialPatient.id == patient_id)
        .with_for_update()
    )
    res = await db.execute(stmt)
    patient = res.scalar_one_or_none()
    if patient is None:
        raise ValueError(f"TrialPatient with id={patient_id} not found.")

    old_status = patient.consent_status.value
    patient.consent_status = ConsentStatus.WITHDRAWN
    await db.flush()

    field_changes = {
        "consent_status": {"old": old_status, "new": ConsentStatus.WITHDRAWN.value},
        "dpdp_revocation": True,
    }
    await append_audit_entry(
        db,
        entity_name="trial_patients",
        entity_id=str(patient.id),
        action_type=AuditAction.UPDATE,
        field_changes=field_changes,
        modified_by=modified_by,
    )

    await db.commit()
    await db.refresh(patient)
    return patient
