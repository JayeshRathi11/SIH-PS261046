"""
AyuTrial-CTMS – Safety (Adverse Event) Service

Business logic for:
- Creating adverse events with pessimistic row-level locking on the patient row.
- Automatic SAE flag + 24-hour SLA deadline when severity is
  HOSPITALIZATION, LIFE_THREATENING, or DEATH (NDCT Rules 2019).
- Writing corresponding ALCOA+ audit ledger entries.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AdverseEvent,
    AEStatus,
    AESeverity,
    AuditAction,
    SAE_SEVERITIES,
    TrialPatient,
)
from app.services.audit import append_audit_entry


SAE_REPORTING_WINDOW_HOURS = 24


async def create_adverse_event(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    severity: AESeverity,
    clinical_notes: Optional[str],
    reported_by: str,
) -> AdverseEvent:
    """
    Create an adverse event record atomically.

    Pessimistic locking:
        SELECT ... FOR UPDATE on the patient row prevents concurrent writes
        (e.g., two coordinators submitting AEs simultaneously for the same patient).

    SAE auto-trigger:
        If severity in {HOSPITALIZATION, LIFE_THREATENING, DEATH}:
            is_serious = True
            sae_clock_start = now()
            sla_deadline   = now() + 24h

    ALCOA+ audit:
        Appends a cryptographically chained ledger entry for this INSERT.
    """
    # ------------------------------------------------------------------
    # 1. Lock patient row (pessimistic concurrency control)
    # ------------------------------------------------------------------
    stmt = (
        select(TrialPatient)
        .where(TrialPatient.id == patient_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    patient: Optional[TrialPatient] = result.scalar_one_or_none()

    if patient is None:
        raise ValueError(f"TrialPatient with id={patient_id} not found.")

    # ------------------------------------------------------------------
    # 2. Determine SAE flags
    # ------------------------------------------------------------------
    now = datetime.now(tz=timezone.utc)
    is_serious = severity in SAE_SEVERITIES
    sae_clock_start: Optional[datetime] = now if is_serious else None
    sla_deadline: Optional[datetime] = (
        now + timedelta(hours=SAE_REPORTING_WINDOW_HOURS) if is_serious else None
    )

    # ------------------------------------------------------------------
    # 3. Persist adverse event
    # ------------------------------------------------------------------
    ae = AdverseEvent(
        patient_id=patient_id,
        severity=severity,
        clinical_notes=clinical_notes,
        is_serious=is_serious,
        sae_clock_start=sae_clock_start,
        sla_deadline=sla_deadline,
        status=AEStatus.OPEN,
        reported_by=reported_by,
        recorded_at=now,
    )
    db.add(ae)
    await db.flush()  # populate ae.id before audit entry

    # ------------------------------------------------------------------
    # 4. Write ALCOA+ audit entry
    # ------------------------------------------------------------------
    field_changes: dict[str, Any] = {
        "patient_id": str(patient_id),
        "severity": severity.value,
        "is_serious": is_serious,
        "clinical_notes": clinical_notes,
        "sae_clock_start": sae_clock_start.isoformat() if sae_clock_start else None,
        "sla_deadline": sla_deadline.isoformat() if sla_deadline else None,
        "status": AEStatus.OPEN.value,
    }

    await append_audit_entry(
        db,
        entity_name="adverse_events",
        entity_id=str(ae.id),
        action_type=AuditAction.INSERT,
        field_changes=field_changes,
        modified_by=reported_by,
    )

    await db.commit()
    await db.refresh(ae)
    return ae
