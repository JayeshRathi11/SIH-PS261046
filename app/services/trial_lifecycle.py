import re
import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AuditAction, ClinicalTrial, TrialStatus
from app.services.audit import append_audit_entry

CTRI_REGEX = re.compile(r"^CTRI/\d{4}/\d{2}/\d{6}$")

VALID_TRANSITIONS = {
    TrialStatus.DRAFT: {TrialStatus.IEC_APPROVED},
    TrialStatus.IEC_APPROVED: {TrialStatus.CTRI_LINKED},
    TrialStatus.CTRI_LINKED: {TrialStatus.RECRUITING},
    TrialStatus.RECRUITING: {TrialStatus.FROZEN, TrialStatus.CLOSED},
    TrialStatus.FROZEN: {TrialStatus.RECRUITING, TrialStatus.CLOSED},
    TrialStatus.CLOSED: set(),
}


class InvalidTransitionError(Exception):
    pass


class InvalidCtriError(Exception):
    pass


class MissingIecError(Exception):
    pass


async def advance_trial_status(
    db: AsyncSession,
    *,
    trial_id: uuid.UUID,
    target_status: TrialStatus,
    iec_clearance_number: Optional[str] = None,
    ctri_registration_id: Optional[str] = None,
    modified_by: str = "investigator",
) -> ClinicalTrial:
    stmt = (
        select(ClinicalTrial)
        .where(ClinicalTrial.id == trial_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    trial = result.scalar_one_or_none()
    if trial is None:
        raise ValueError(f"ClinicalTrial with id={trial_id} not found.")

    current_status = trial.status
    allowed = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise InvalidTransitionError(
            f"Invalid status transition from {current_status.value} to {target_status.value}. Allowed: {[s.value for s in allowed]}"
        )

    if target_status == TrialStatus.IEC_APPROVED:
        clearance = iec_clearance_number or trial.iec_clearance_number
        if not clearance or not clearance.strip():
            raise MissingIecError("Transition to IEC_APPROVED requires a valid iec_clearance_number.")
        trial.iec_clearance_number = clearance.strip()

    elif target_status == TrialStatus.CTRI_LINKED:
        ctri_id = ctri_registration_id or trial.ctri_registration_id
        if not ctri_id or not CTRI_REGEX.match(ctri_id.strip()):
            raise InvalidCtriError(
                f"Invalid CTRI registration ID format '{ctri_id}'. Required format: CTRI/YYYY/MM/NNNNNN"
            )
        trial.ctri_registration_id = ctri_id.strip()

    old_status = trial.status.value
    trial.status = target_status
    await db.flush()

    field_changes = {
        "status": {"old": old_status, "new": target_status.value},
        "iec_clearance_number": trial.iec_clearance_number,
        "ctri_registration_id": trial.ctri_registration_id,
    }

    await append_audit_entry(
        db,
        entity_name="clinical_trials",
        entity_id=str(trial.id),
        action_type=AuditAction.UPDATE,
        field_changes=field_changes,
        modified_by=modified_by,
    )

    await db.commit()
    await db.refresh(trial)
    return trial
