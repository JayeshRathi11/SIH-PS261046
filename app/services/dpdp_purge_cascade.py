import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AdverseEvent,
    AEStatus,
    AuditAction,
    ConsentStatus,
    ECRFRecord,
    TrialPatient,
)
from app.services.audit import append_audit_entry

DEFAULT_DPDP_SALT = "AyuTrial-DPDP-Salt-2026"


async def execute_dpdp_purge_cascade(
    patient_id: uuid.UUID,
    db: AsyncSession,
    salt: str = DEFAULT_DPDP_SALT,
) -> Dict[str, Any]:
    # 1. Fetch patient
    stmt = select(TrialPatient).where(TrialPatient.id == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    if patient is None:
        raise ValueError(f"TrialPatient with id={patient_id} not found.")

    original_usubjid = patient.usubjid

    # 2. Set consent status to WITHDRAWN
    patient.consent_status = ConsentStatus.WITHDRAWN

    # 3. Generate salted cryptographic pseudonym
    hashed = hashlib.sha256((original_usubjid + salt).encode("utf-8")).hexdigest()[:12]
    pseudonym = f"ANONYMIZED_{hashed}"
    patient.usubjid = pseudonym

    # 4. Nullify communication channels (PII erasure)
    patient.telegram_chat_id = None

    # 5. Quarantine eCRF records
    stmt_ecrf = select(ECRFRecord).where(ECRFRecord.patient_id == patient_id)
    ecrf_res = await db.execute(stmt_ecrf)
    ecrfs = ecrf_res.scalars().all()
    for ecrf in ecrfs:
        current_data = ecrf.form_data or {}
        ecrf.form_data = {
            **current_data,
            "is_dpdp_quarantined": True,
            "pii_redacted": True,
            "quarantined_at": datetime.now(timezone.utc).isoformat(),
        }

    # 6. Quarantine Adverse Events
    stmt_ae = select(AdverseEvent).where(AdverseEvent.patient_id == patient_id)
    ae_res = await db.execute(stmt_ae)
    aes = ae_res.scalars().all()
    for ae in aes:
        ae.clinical_notes = "[REDACTED - DPDP CONSENT WITHDRAWN PURGE]"
        ae.concomitant_drugs = []
        ae.status = AEStatus.CLOSED

    # 7. Commit immutable ACTION_PURGE_CASCADE to ALCOA+ Audit Ledger
    audit_entry = await append_audit_entry(
        db,
        entity_name="trial_patients",
        entity_id=str(patient.id),
        action_type=AuditAction.UPDATE,
        field_changes={
            "event": "ACTION_PURGE_CASCADE",
            "pseudonym": pseudonym,
            "consent_status": "WITHDRAWN",
            "telegram_purged": True,
            "ecrf_records_quarantined": len(ecrfs),
            "adverse_events_quarantined": len(aes),
            "purge_timestamp": datetime.now(timezone.utc).isoformat(),
        },
        modified_by="dpdp_compliance_officer",
    )

    await db.commit()
    await db.refresh(patient)

    return {
        "status": "PURGE_CASCADE_EXECUTED",
        "patient_id": str(patient.id),
        "pseudonym": pseudonym,
        "consent_status": "WITHDRAWN",
        "telegram_purged": True,
        "ecrf_records_quarantined": len(ecrfs),
        "adverse_events_quarantined": len(aes),
        "alcoa_audit_sequence_id": audit_entry.sequence_id,
    }
