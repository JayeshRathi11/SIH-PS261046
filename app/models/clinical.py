"""
AyuTrial-CTMS – SQLAlchemy ORM Models
All clinical trial domain entities with proper enums and constraints.
Uses Optional[X] syntax (not X | None) for Python 3.14 compatibility
with SQLAlchemy 2.0 mapped column type introspection.
"""
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class TrialStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    IEC_APPROVED = "IEC_APPROVED"
    CTRI_LINKED = "CTRI_LINKED"
    RECRUITING = "RECRUITING"
    FROZEN = "FROZEN"
    CLOSED = "CLOSED"


class ConsentStatus(str, enum.Enum):
    PENDING = "PENDING"
    OBTAINED = "OBTAINED"
    WITHDRAWN = "WITHDRAWN"


class AESeverity(str, enum.Enum):
    MILD = "MILD"
    MODERATE = "MODERATE"
    SEVERE = "SEVERE"
    HOSPITALIZATION = "HOSPITALIZATION"
    LIFE_THREATENING = "LIFE_THREATENING"
    DEATH = "DEATH"


class AEStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    REPORTED_TO_CDSCO = "REPORTED_TO_CDSCO"
    CLOSED = "CLOSED"


class AuditAction(str, enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"


# ---------------------------------------------------------------------------
# SAE severities set (used by business logic)
# ---------------------------------------------------------------------------
SAE_SEVERITIES: frozenset = frozenset(
    {AESeverity.HOSPITALIZATION, AESeverity.LIFE_THREATENING, AESeverity.DEATH}
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class TrialSite(Base):
    """Represents a clinical trial participating center / site."""

    __tablename__ = "trial_sites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    site_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    patients: Mapped[list["TrialPatient"]] = relationship("TrialPatient", back_populates="site")


class ClinicalTrial(Base):
    """Represents a single AIIA clinical trial protocol."""

    __tablename__ = "clinical_trials"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    protocol_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    ctri_registration_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    iec_clearance_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    study_title: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[TrialStatus] = mapped_column(
        Enum(TrialStatus, name="trial_status_enum"), nullable=False, default=TrialStatus.DRAFT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    patients: Mapped[list["TrialPatient"]] = relationship(
        "TrialPatient", back_populates="trial", cascade="all, delete-orphan"
    )
    ecrf_records: Mapped[list["ECRFRecord"]] = relationship(
        "ECRFRecord", back_populates="trial", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_clinical_trials_status", "status"),)


class TrialPatient(Base):
    """A patient enrolled in a specific clinical trial."""

    __tablename__ = "trial_patients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    trial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinical_trials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    site_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_sites.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # CDISC Unique Subject Identifier
    usubjid: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    # Ayurvedic phenotypic markers
    prakriti_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    baseline_agni: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    consent_status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus, name="consent_status_enum"),
        nullable=False,
        default=ConsentStatus.PENDING,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    trial: Mapped["ClinicalTrial"] = relationship("ClinicalTrial", back_populates="patients")
    site: Mapped[Optional["TrialSite"]] = relationship("TrialSite", back_populates="patients")
    adverse_events: Mapped[list["AdverseEvent"]] = relationship(
        "AdverseEvent", back_populates="patient", cascade="all, delete-orphan"
    )
    ecrf_records: Mapped[list["ECRFRecord"]] = relationship(
        "ECRFRecord", back_populates="patient", cascade="all, delete-orphan"
    )
    access_logs: Mapped[list["AccessAuditLog"]] = relationship(
        "AccessAuditLog", back_populates="patient", cascade="all, delete-orphan"
    )
    adherence_logs: Mapped[list["PatientAdherenceLog"]] = relationship(
        "PatientAdherenceLog", back_populates="patient", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("trial_id", "usubjid", name="uq_patient_trial_usubjid"),
    )


class AdverseEvent(Base):
    """
    Adverse event record with 24-hour SAE SLA clock.
    NDCT Rules 2019 mandates SAE reporting within 24 hours to CDSCO.
    """

    __tablename__ = "adverse_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clinical_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[AESeverity] = mapped_column(
        Enum(AESeverity, name="ae_severity_enum"), nullable=False
    )
    ayurvedic_intervention: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    concomitant_drugs: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    herb_drug_conflicts: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    coded_meddra_terms: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    form_ct16_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # SAE flags – automatically set by business logic
    is_serious: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sae_clock_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[AEStatus] = mapped_column(
        Enum(AEStatus, name="ae_status_enum"), nullable=False, default=AEStatus.OPEN
    )
    reported_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    patient: Mapped["TrialPatient"] = relationship("TrialPatient", back_populates="adverse_events")

    __table_args__ = (
        Index("ix_ae_is_serious_status", "is_serious", "status"),
        Index("ix_ae_sla_deadline", "sla_deadline"),
    )


class ECRFRecord(Base):
    __tablename__ = "ecrf_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinical_trials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    site_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_sites.id", ondelete="SET NULL"), nullable=True, index=True
    )
    visit_number: Mapped[int] = mapped_column(Integer, nullable=False)
    visit_name: Mapped[str] = mapped_column(String(100), nullable=False)
    form_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    patient: Mapped["TrialPatient"] = relationship("TrialPatient", back_populates="ecrf_records")
    trial: Mapped["ClinicalTrial"] = relationship("ClinicalTrial", back_populates="ecrf_records")

    __table_args__ = (
        UniqueConstraint("patient_id", "visit_number", name="uq_patient_visit_number"),
        Index("ix_ecrf_patient_visit", "patient_id", "visit_number"),
    )


class AccessAuditLog(Base):
    """
    DPDP Act 2023 Read-Access Audit Trail.
    Logs sensitive clinical record reads / inspections with user ID and purpose code.
    """

    __tablename__ = "access_audit_logs"

    access_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    purpose_code: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    patient: Mapped["TrialPatient"] = relationship("TrialPatient", back_populates="access_logs")

    __table_args__ = (
        Index("ix_access_audit_patient_time", "patient_id", "accessed_at"),
    )


class AlcoaAuditLedger(Base):
    """
    Immutable, cryptographically chained audit ledger (ALCOA+ compliant).
    Each row links to its predecessor via SHA-256 hash chaining.
    Application role does NOT have UPDATE/DELETE on this table (enforced by DDL).
    """

    __tablename__ = "alcoa_audit_ledger"

    sequence_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action_type: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action_enum"), nullable=False
    )
    field_changes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    modified_by: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    __table_args__ = (
        Index("ix_audit_entity_name_id", "entity_name", "entity_id"),
    )


class DeadLetterExport(Base):
    """
    Self-Healing Dead-Letter Export Retry Queue.
    Isolates corrupted or unmapped patient records during batch export
    without interrupting the clinical study export pipeline.
    """

    __tablename__ = "dead_letter_exports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trial_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("clinical_trials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    record_identifier: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    payload_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    error_trace: Mapped[str] = mapped_column(Text, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ISOLATED")
    quarantined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class PatientAdherenceLog(Base):
    """
    Real-Time Patient Medication Adherence Log.
    Tracks compliance via Telegram Bot interactive reminders or manual clinics.
    """

    __tablename__ = "patient_adherence_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("trial_patients.id", ondelete="CASCADE"), nullable=False, index=True
    )
    telegram_chat_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    dosage_status: Mapped[str] = mapped_column(String(20), nullable=False)
    reported_via: Mapped[str] = mapped_column(String(50), nullable=False, default="TELEGRAM_BOT")
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    patient: Mapped["TrialPatient"] = relationship("TrialPatient", back_populates="adherence_logs")

