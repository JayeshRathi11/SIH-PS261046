"""
AyuTrial-CTMS – Safety (Adverse Event) Service

Business logic for:
- Creating adverse events with pessimistic row-level locking on the patient row.
- Automatic SAE flag + 24-hour SLA deadline when severity is
  HOSPITALIZATION, LIFE_THREATENING, or DEATH (NDCT Rules 2019).
- NPvCC Pharmacovigilance: Ayurvedic herb-drug interaction checking & MedDRA term extraction.
- Writing corresponding ALCOA+ audit ledger entries.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional
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
from app.services.herb_matrix import check_herb_drug_interactions
from app.services.meddra_coder import extract_meddra_terms
from app.services.analytics_service import invalidate_kpi_cache


SAE_REPORTING_WINDOW_HOURS = 24


async def create_adverse_event(
    db: AsyncSession,
    *,
    patient_id: uuid.UUID,
    severity: AESeverity,
    clinical_notes: Optional[str],
    ayurvedic_intervention: Optional[str] = None,
    concomitant_drugs: Optional[List[str]] = None,
    reported_by: str,
) -> AdverseEvent:
    stmt = (
        select(TrialPatient)
        .where(TrialPatient.id == patient_id)
        .with_for_update()
    )
    result = await db.execute(stmt)
    patient: Optional[TrialPatient] = result.scalar_one_or_none()
    if patient is None:
        raise ValueError(f"TrialPatient with id={patient_id} not found.")

    drug_list = concomitant_drugs or []
    now = datetime.now(tz=timezone.utc)
    is_serious = severity in SAE_SEVERITIES
    sae_clock_start = now if is_serious else None
    sla_deadline = (
        now + timedelta(hours=SAE_REPORTING_WINDOW_HOURS) if is_serious else None
    )

    conflicts = []
    if ayurvedic_intervention:
        conflicts = check_herb_drug_interactions(ayurvedic_intervention, drug_list)

    meddra = extract_meddra_terms(clinical_notes or "")
    has_conflict = bool(conflicts)
    form_ct16_available = is_serious

    ae = AdverseEvent(
        patient_id=patient_id,
        severity=severity,
        clinical_notes=clinical_notes,
        ayurvedic_intervention=ayurvedic_intervention,
        concomitant_drugs=drug_list,
        herb_drug_conflicts=conflicts,
        coded_meddra_terms=meddra,
        has_conflict=has_conflict,
        form_ct16_available=form_ct16_available,
        is_serious=is_serious,
        sae_clock_start=sae_clock_start,
        sla_deadline=sla_deadline,
        status=AEStatus.OPEN,
        reported_by=reported_by,
        recorded_at=now,
    )
    db.add(ae)
    await db.flush()

    field_changes: dict[str, Any] = {
        "patient_id": str(patient_id),
        "severity": severity.value,
        "is_serious": is_serious,
        "clinical_notes": clinical_notes,
        "ayurvedic_intervention": ayurvedic_intervention,
        "concomitant_drugs": drug_list,
        "herb_drug_conflicts": conflicts,
        "coded_meddra_terms": meddra,
        "has_conflict": has_conflict,
        "form_ct16_available": form_ct16_available,
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
    if is_serious:
        invalidate_kpi_cache()
        try:
            from app.routers.websockets import broadcast_sae_alert
            await broadcast_sae_alert(ae)
        except Exception:
            pass
    return ae
