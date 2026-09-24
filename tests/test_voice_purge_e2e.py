import asyncio
import io
import wave
import uuid
import zipfile
from datetime import datetime, timezone

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AdverseEvent,
    AESeverity,
    AEStatus,
    AlcoaAuditLedger,
    ClinicalTrial,
    ConsentStatus,
    ECRFRecord,
    TrialPatient,
    TrialStatus,
)
from app.services.dpdp_purge_cascade import execute_dpdp_purge_cascade
from app.services.voice_transcriber import transcribe_clinical_audio


def create_test_wav_bytes(embedded_note: str = "") -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 16000 samples of 16-bit PCM = 1 second
        wf.writeframes(b"\x00\x00" * 16000)
    raw = buf.getvalue()
    if embedded_note:
        raw += f"\nCLINICAL_NOTE: {embedded_note}".encode("utf-8")
    return raw


async def seed_master_trial_and_patient(db: AsyncSession) -> tuple[ClinicalTrial, TrialPatient]:
    trial = ClinicalTrial(
        protocol_id=f"AIIA-MASTER-{uuid.uuid4().hex[:6].upper()}",
        study_title="AIIA Master Lifecycle Clinical Trial",
        status=TrialStatus.RECRUITING,
    )
    db.add(trial)
    await db.flush()

    patient = TrialPatient(
        trial_id=trial.id,
        usubjid=f"USJ-{uuid.uuid4().hex[:6].upper()}",
        prakriti_type="PITTA",
        baseline_agni="TIKSHNA",
        consent_status=ConsentStatus.OBTAINED,
        telegram_chat_id="tg_master_12345",
    )
    db.add(patient)
    await db.commit()
    await db.refresh(trial)
    await db.refresh(patient)
    return trial, patient


# ===========================================================================
# GROUP A: Multilingual Voice-to-Text Clinical Audio Pipeline (Feature 9)
# ===========================================================================
class TestVoiceTranscriberPipeline:

    async def test_transcribe_audio_endpoint_with_ayurvedic_terms(
        self, client: httpx.AsyncClient
    ):
        note = "Subject presented with netra-peetata and severe amlapitta after Guduchi"
        wav_bytes = create_test_wav_bytes(note)

        files = {
            "audio_file": ("consultation_record.wav", wav_bytes, "audio/wav")
        }
        resp = await client.post("/api/v1/safety/transcribe-audio", files=files)
        assert resp.status_code == 200
        data = resp.json()

        assert "transcribed_text" in data
        assert "netra-peetata" in data["transcribed_text"]
        assert "amlapitta" in data["transcribed_text"]
        assert data["audio_duration_seconds"] >= 1.0
        assert data["detected_language"] == "hi-IN/en-IN"

        # Check auto-coded MedDRA terms
        meddra = data["coded_meddra_terms"]
        pts = [m["preferred_term"] for m in meddra]
        assert "Jaundice ocular" in pts
        assert "Heartburn" in pts

    async def test_transcribe_audio_filename_heuristic_fallback(
        self, client: httpx.AsyncClient
    ):
        wav_bytes = create_test_wav_bytes()  # No embedded text
        files = {
            "audio_file": ("clinic_yakrit_shotha_case.wav", wav_bytes, "audio/wav")
        }
        resp = await client.post("/api/v1/safety/transcribe-audio", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert "yakrit shotha" in data["transcribed_text"]
        pts = [m["preferred_term"] for m in data["coded_meddra_terms"]]
        assert "Hepatosplenomegaly" in pts

    async def test_empty_audio_upload_returns_400(self, client: httpx.AsyncClient):
        files = {
            "audio_file": ("empty.wav", b"", "audio/wav")
        }
        resp = await client.post("/api/v1/safety/transcribe-audio", files=files)
        assert resp.status_code == 400


# ===========================================================================
# GROUP B: DPDP Purge & Pseudonymization Cascade (Feature 24 Hardening)
# ===========================================================================
class TestDpdpPurgeCascade:

    async def test_dpdp_purge_endpoint_execution(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_master_trial_and_patient(db_session)
        orig_usubjid = patient.usubjid

        # Seed linked eCRF and AE
        ecrf = ECRFRecord(
            patient_id=patient.id,
            trial_id=trial.id,
            visit_number=1,
            visit_name="Baseline Visit",
            form_data={"systolic_bp": 120, "patient_name": "Confidential Person"},
        )
        db_session.add(ecrf)

        ae = AdverseEvent(
            patient_id=patient.id,
            clinical_notes="Confidential details of adverse event",
            severity=AESeverity.HOSPITALIZATION,
            is_serious=True,
            status=AEStatus.OPEN,
            concomitant_drugs=["Aspirin 75mg"],
            herb_drug_conflicts=[],
            coded_meddra_terms=[],
            has_conflict=False,
            form_ct16_available=True,
        )
        db_session.add(ae)
        await db_session.commit()

        # Execute DPDP Purge Cascade
        resp = await client.post(f"/api/v1/patients/{patient.id}/dpdp-purge")
        assert resp.status_code == 200
        data = resp.json()

        assert data["status"] == "PURGE_CASCADE_EXECUTED"
        assert data["consent_status"] == "WITHDRAWN"
        assert data["telegram_purged"] is True
        assert data["pseudonym"].startswith("ANONYMIZED_")
        assert data["pseudonym"] != orig_usubjid
        assert data["ecrf_records_quarantined"] == 1
        assert data["adverse_events_quarantined"] == 1

        # Check DB state
        await db_session.refresh(patient)
        assert patient.consent_status == ConsentStatus.WITHDRAWN
        assert patient.usubjid.startswith("ANONYMIZED_")
        assert patient.telegram_chat_id is None

        await db_session.refresh(ecrf)
        assert ecrf.form_data.get("is_dpdp_quarantined") is True
        assert ecrf.form_data.get("pii_redacted") is True

        await db_session.refresh(ae)
        assert "[REDACTED - DPDP CONSENT WITHDRAWN PURGE]" in ae.clinical_notes
        assert ae.concomitant_drugs == []
        assert ae.status == AEStatus.CLOSED

        # Check export exclusion: FHIR export must return 404
        fhir_resp = await client.get(f"/api/v1/export/fhir-bundle/{patient.id}")
        assert fhir_resp.status_code == 404

        # Check export exclusion: CDISC export excludes the withdrawn patient
        cdisc_resp = await client.get(f"/api/v1/export/cdisc-sdtm/{trial.id}")
        # Since all patients in this trial were withdrawn, returns 404 (no active patients)
        assert cdisc_resp.status_code == 404

        # Verify ALCOA+ Audit Ledger integrity
        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        assert verify_resp.json()["status"] == "VERIFIED_SECURE"
        assert verify_resp.json()["tamper_detected"] is False


# ===========================================================================
# GROUP C: Grand Slam 24-Feature Full Clinical Lifecycle Integration
# ===========================================================================
class TestGrandSlamClinicalLifecycle:

    async def test_complete_regulatory_trial_lifecycle_e2e(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        # 1. Register Clinical Trial (Draft)
        proto_id = f"AIIA-GUD-{uuid.uuid4().hex[:6].upper()}"
        trial_resp = await client.post(
            "/api/v1/trials",
            json={
                "protocol_id": proto_id,
                "study_title": "Grand Slam Full-Lifecycle E2E Trial",
                "status": "DRAFT",
            },
        )
        assert trial_resp.status_code == 201
        trial_id = trial_resp.json()["id"]

        # 2. Advance to IEC_APPROVED
        iec_resp = await client.post(
            f"/api/v1/trials/{trial_id}/advance-status",
            json={
                "target_status": "IEC_APPROVED",
                "iec_clearance_number": "IEC/AIIA/2026/GRAND-SLAM",
            },
        )
        assert iec_resp.status_code == 200
        assert iec_resp.json()["status"] == "IEC_APPROVED"

        # 3. Advance to CTRI_LINKED with statutory regex CTRI/YYYY/MM/NNNNNN
        ctri_resp = await client.post(
            f"/api/v1/trials/{trial_id}/advance-status",
            json={
                "target_status": "CTRI_LINKED",
                "ctri_registration_id": "CTRI/2026/05/012345",
            },
        )
        assert ctri_resp.status_code == 200
        assert ctri_resp.json()["status"] == "CTRI_LINKED"

        # 4. Advance to RECRUITING
        rec_resp = await client.post(
            f"/api/v1/trials/{trial_id}/advance-status",
            json={"target_status": "RECRUITING"},
        )
        assert rec_resp.status_code == 200
        assert rec_resp.json()["status"] == "RECRUITING"

        # 5. Enroll Patient with DPDP Consent
        pat_resp = await client.post(
            "/api/v1/patients",
            json={
                "trial_id": trial_id,
                "usubjid": f"GS-{uuid.uuid4().hex[:6].upper()}",
                "prakriti_type": "PITTA_KAPHA",
                "baseline_agni": "TIKSHNA",
                "consent_status": "OBTAINED",
            },
        )
        assert pat_resp.status_code == 201
        patient_id = pat_resp.json()["id"]

        # 6. Concurrency Field Locking on eCRF
        lock_resp = await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": f"ecrf_{patient_id}_v1",
                "field_name": "systolic_bp",
                "user_id": "dr_vaidya",
                "ttl_seconds": 30,
            },
        )
        assert lock_resp.status_code == 200

        # Contention by coordinator
        contend_resp = await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": f"ecrf_{patient_id}_v1",
                "field_name": "systolic_bp",
                "user_id": "coord_sharma",
            },
        )
        assert contend_resp.status_code == 423

        # Release lock
        await client.post(
            "/api/v1/locks/release",
            json={
                "record_id": f"ecrf_{patient_id}_v1",
                "field_name": "systolic_bp",
                "user_id": "dr_vaidya",
            },
        )

        # 7. Submit eCRF Visit 1
        ecrf_resp = await client.post(
            f"/api/v1/patients/{patient_id}/ecrf",
            json={
                "visit_number": 1,
                "visit_name": "Day 0 - Baseline",
                "form_data": {
                    "systolic_bp": 132,
                    "diastolic_bp": 86,
                    "heart_rate": 78,
                    "active_intervention": "Guduchi Extract 500mg BD",
                    "concomitant_medications": ["Aspirin 75mg OD"],
                },
                "modified_by": "dr_vaidya",
            },
        )
        assert ecrf_resp.status_code == 201

        # 8. Trigger Serious Adverse Event (Guduchi + Aspirin) with Idempotency Key
        idem_key = f"GS-IDEM-{uuid.uuid4().hex[:8]}"
        sae_resp = await client.post(
            "/api/v1/safety/adverse-event",
            headers={"X-Idempotency-Key": idem_key},
            json={
                "patient_id": patient_id,
                "severity": "HOSPITALIZATION",
                "clinical_notes": "Subject developed netra-peetata, dark stool, and severe amlapitta.",
                "ayurvedic_intervention": "Guduchi Extract 500mg BD",
                "concomitant_drugs": ["Aspirin 75mg OD"],
                "reported_by": "dr_vaidya",
            },
        )
        assert sae_resp.status_code == 201
        sae_data = sae_resp.json()
        assert sae_data["is_serious"] is True
        assert sae_data["has_conflict"] is True
        assert len(sae_data["herb_drug_conflicts"]) >= 1
        assert sae_data["herb_drug_conflicts"][0]["drug"] == "Aspirin"
        ae_id = sae_data["id"]

        # 9. Verify Idempotency Shield Rejection
        dup_resp = await client.post(
            "/api/v1/safety/adverse-event",
            headers={"X-Idempotency-Key": idem_key},
            json={
                "patient_id": patient_id,
                "severity": "HOSPITALIZATION",
                "clinical_notes": "Duplicate payload",
                "reported_by": "dr_vaidya",
            },
        )
        assert dup_resp.status_code == 409

        # 10. Generate CDSCO Form CT-16 PDF
        ct16_resp = await client.get(f"/api/v1/safety/reports/ct16/{ae_id}")
        assert ct16_resp.status_code == 200
        assert ct16_resp.headers["content-type"] == "application/pdf"
        assert len(ct16_resp.content) > 1000

        # 11. Download CDISC SDTM ZIP Tabulation Package
        cdisc_resp = await client.get(f"/api/v1/export/cdisc-sdtm/{trial_id}")
        assert cdisc_resp.status_code == 200
        assert cdisc_resp.headers["content-type"] == "application/zip"
        
        # Verify ZIP contains dm.csv, vs.csv, ae.csv, define.xml
        zip_file = zipfile.ZipFile(io.BytesIO(cdisc_resp.content))
        names = zip_file.namelist()
        assert "dm.csv" in names
        assert "vs.csv" in names
        assert "ae.csv" in names
        assert "define.xml" in names

        # 12. Notarize Isolated Merkle Root & Verify Cryptographic Audit Chain
        merkle_resp = await client.post("/api/v1/audit/notarize-witness")
        assert merkle_resp.status_code == 200
        assert "merkle_root" in merkle_resp.json()

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        vdata = verify_resp.json()
        assert vdata["status"] == "VERIFIED_SECURE"
        assert vdata["tamper_detected"] is False
        assert vdata["total_blocks"] > 0
