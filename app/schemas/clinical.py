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
    iec_clearance_number: str | None = None
    study_title: str = Field(..., max_length=500)
    status: TrialStatus = TrialStatus.DRAFT


class ClinicalTrialOut(BaseModel):
    id: uuid.UUID
    protocol_id: str
    ctri_registration_id: str | None
    iec_clearance_number: str | None = None
    study_title: str
    status: TrialStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdvanceStatusPayload(BaseModel):
    target_status: TrialStatus
    iec_clearance_number: str | None = None
    ctri_registration_id: str | None = None
    modified_by: str = Field("investigator", max_length=100)


# ---------------------------------------------------------------------------
# Trial Site
# ---------------------------------------------------------------------------
class TrialSiteCreate(BaseModel):
    site_code: str = Field(..., max_length=50)
    site_name: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    is_active: bool = True


class TrialSiteOut(BaseModel):
    id: uuid.UUID
    site_code: str
    site_name: str
    city: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Trial Patient
# ---------------------------------------------------------------------------
class TrialPatientCreate(BaseModel):
    trial_id: uuid.UUID
    usubjid: str = Field(..., max_length=50)
    site_id: uuid.UUID | None = None
    prakriti_type: str | None = None
    baseline_agni: str | None = None
    consent_status: ConsentStatus = ConsentStatus.OBTAINED


class TrialPatientOut(BaseModel):
    id: uuid.UUID
    trial_id: uuid.UUID
    usubjid: str
    site_id: uuid.UUID | None = None
    prakriti_type: str | None = None
    baseline_agni: str | None = None
    consent_status: ConsentStatus
    enrolled_at: datetime

    model_config = {"from_attributes": True}


class ConsentRevokeOut(BaseModel):
    patient_id: uuid.UUID
    usubjid: str
    consent_status: ConsentStatus
    revoked_at: datetime


# ---------------------------------------------------------------------------
# Adverse Event
# ---------------------------------------------------------------------------
class AdverseEventCreate(BaseModel):
    patient_id: uuid.UUID
    severity: AESeverity
    clinical_notes: str | None = None
    ayurvedic_intervention: str | None = None
    concomitant_drugs: list[str] = []
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
    herb_drug_conflicts: list[dict] = []
    coded_meddra_terms: list[dict] = []
    has_conflict: bool = False
    form_ct16_available: bool = False

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Audit Chain Verification
# ---------------------------------------------------------------------------
class ChainVerificationOut(BaseModel):
    status: str   # VERIFIED_SECURE | TAMPER_DETECTED
    total_blocks: int
    tampered_sequence_ids: list[int]
    reason: str | None = None
    tamper_detected: bool = False
    local_merkle_root: str | None = None
    witness_merkle_root: str | None = None



# ---------------------------------------------------------------------------
# Electronic Case Report Form (eCRF)
# ---------------------------------------------------------------------------
class ECRFRecordCreate(BaseModel):
    visit_number: int = Field(..., ge=1, description="Sequential visit index (1, 2, 3...)")
    visit_name: str = Field(..., max_length=100, description="Visit descriptor, e.g. Day 0, Day 14")
    form_data: dict[str, Any] = Field(default_factory=dict, description="Hybrid biomarkers and clinical findings")
    modified_by: str = Field("investigator", max_length=100, description="User recording the eCRF")


class ECRFRecordOut(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    trial_id: uuid.UUID
    visit_number: int
    visit_name: str
    form_data: dict[str, Any]
    recorded_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Access Audit Log (DPDP Read Audit)
# ---------------------------------------------------------------------------
class AccessAuditLogOut(BaseModel):
    access_id: int
    user_id: str
    patient_id: uuid.UUID
    purpose_code: str
    ip_address: str | None = None
    accessed_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Portfolio & Executive KPI Analytics
# ---------------------------------------------------------------------------
class PortfolioKPIsOut(BaseModel):
    trial_portfolio: dict[str, Any]
    patient_metrics: dict[str, Any]
    safety_kpis: dict[str, Any]
    compliance_rate: float
    cached: bool = False
    generated_at: datetime

