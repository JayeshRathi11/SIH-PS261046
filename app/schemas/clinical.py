"""
AyuTrial-CTMS – Pydantic Request/Response Schemas
"""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.clinical import AESeverity, AEStatus, TrialStatus, ConsentStatus


# ---------------------------------------------------------------------------
# Clinical Trial
# ---------------------------------------------------------------------------
class ClinicalTrialCreate(BaseModel):
    protocol_id: str = Field(..., max_length=100)
    ctri_registration_id: str | None = None
    study_title: str = Field(..., max_length=500)
    status: TrialStatus = TrialStatus.DRAFT


class ClinicalTrialOut(BaseModel):
    id: uuid.UUID
    protocol_id: str
    ctri_registration_id: str | None
    study_title: str
    status: TrialStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Trial Patient
# ---------------------------------------------------------------------------
class TrialPatientCreate(BaseModel):
    trial_id: uuid.UUID
    usubjid: str = Field(..., max_length=50)
    prakriti_type: str | None = None
    baseline_agni: str | None = None
    consent_status: ConsentStatus = ConsentStatus.PENDING


class TrialPatientOut(BaseModel):
    id: uuid.UUID
    trial_id: uuid.UUID
    usubjid: str
    prakriti_type: str | None
    baseline_agni: str | None
    consent_status: ConsentStatus
    enrolled_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Adverse Event
# ---------------------------------------------------------------------------
class AdverseEventCreate(BaseModel):
    patient_id: uuid.UUID
    severity: AESeverity
    clinical_notes: str | None = None
    reported_by: str = Field(..., max_length=100, description="User ID / username of reporter")


class AdverseEventOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    severity: AESeverity
    is_serious: bool
    clinical_notes: str | None
    sae_clock_start: datetime | None
    sla_deadline: datetime | None
    status: AEStatus
    reported_by: str | None
    recorded_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Audit Chain Verification
# ---------------------------------------------------------------------------
class ChainVerificationOut(BaseModel):
    status: str   # VERIFIED_SECURE | TAMPER_DETECTED
    total_blocks: int
    tampered_sequence_ids: list[int]
