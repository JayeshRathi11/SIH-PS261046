import uuid
import httpx
import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AlcoaAuditLedger,
    ClinicalTrial,
    ConsentStatus,
    TrialPatient,
    TrialStatus,
)
from app.services.audit import _compute_hash
from app.services.merkle import build_merkle_tree, notarize_current_ledger, set_notarized_root


class TestProtocolLifecycleAndCtriValidation:

    async def test_cannot_enroll_patient_in_draft_or_iec_approved_trial(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-PROTO-{uuid.uuid4().hex[:6].upper()}",
            study_title="Ashwagandha Anxiety Protocol",
            status=TrialStatus.DRAFT,
        )
        db_session.add(trial)
        await db_session.commit()
        await db_session.refresh(trial)

        enroll_payload = {
            "trial_id": str(trial.id),
            "usubjid": f"SUBJ-{uuid.uuid4().hex[:4].upper()}",
            "prakriti_type": "VATA",
            "baseline_agni": "MANDAGNI",
        }
        draft_resp = await client.post("/api/v1/patients", json=enroll_payload)
        assert draft_resp.status_code == 400
        assert "not active for enrollment" in draft_resp.json()["detail"]

        advance_iec = await client.put(
            f"/api/v1/trials/{trial.id}/advance-status",
            json={
                "target_status": "IEC_APPROVED",
                "iec_clearance_number": "IEC/AIIA/2026/044",
            },
        )
        assert advance_iec.status_code == 200
        assert advance_iec.json()["status"] == "IEC_APPROVED"

        iec_enroll_resp = await client.post("/api/v1/patients", json=enroll_payload)
        assert iec_enroll_resp.status_code == 400
        assert "not active for enrollment" in iec_enroll_resp.json()["detail"]

    async def test_invalid_ctri_format_rejected_with_422(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-PROTO-{uuid.uuid4().hex[:6].upper()}",
            study_title="Guduchi Safety Trial",
            iec_clearance_number="IEC/AIIA/2026/099",
            status=TrialStatus.IEC_APPROVED,
        )
        db_session.add(trial)
        await db_session.commit()
        await db_session.refresh(trial)

        resp_invalid_1 = await client.put(
            f"/api/v1/trials/{trial.id}/advance-status",
            json={
                "target_status": "CTRI_LINKED",
                "ctri_registration_id": "CTRI/INVALID",
            },
        )
        assert resp_invalid_1.status_code == 422

        resp_invalid_2 = await client.put(
            f"/api/v1/trials/{trial.id}/advance-status",
            json={
                "target_status": "CTRI_LINKED",
                "ctri_registration_id": "CTRI/2026/4/123",
            },
        )
        assert resp_invalid_2.status_code == 422

    async def test_valid_ctri_advances_to_recruiting_and_enrolls_patient(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-PROTO-{uuid.uuid4().hex[:6].upper()}",
            study_title="Haritaki Metabolic Trial",
            iec_clearance_number="IEC/AIIA/2026/101",
            status=TrialStatus.IEC_APPROVED,
        )
        db_session.add(trial)
        await db_session.commit()
        await db_session.refresh(trial)

        ctri_resp = await client.put(
            f"/api/v1/trials/{trial.id}/advance-status",
            json={
                "target_status": "CTRI_LINKED",
                "ctri_registration_id": "CTRI/2026/04/091234",
            },
        )
        assert ctri_resp.status_code == 200
        assert ctri_resp.json()["status"] == "CTRI_LINKED"
        assert ctri_resp.json()["ctri_registration_id"] == "CTRI/2026/04/091234"

        recruiting_resp = await client.put(
            f"/api/v1/trials/{trial.id}/advance-status",
            json={"target_status": "RECRUITING"},
        )
        assert recruiting_resp.status_code == 200
        assert recruiting_resp.json()["status"] == "RECRUITING"

        usubjid = f"SUBJ-{uuid.uuid4().hex[:6].upper()}"
        enroll_resp = await client.post(
            "/api/v1/patients",
            json={
                "trial_id": str(trial.id),
                "usubjid": usubjid,
                "prakriti_type": "KAPHA",
                "baseline_agni": "SAMAGNI",
            },
        )
        assert enroll_resp.status_code == 201
        patient_data = enroll_resp.json()
        assert patient_data["usubjid"] == usubjid
        assert patient_data["consent_status"] == "OBTAINED"


class TestDpdpConsentLifecycleAndQuarantine:

    async def test_consent_revocation_prevents_subsequent_ecrf(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-DPDP-{uuid.uuid4().hex[:6].upper()}",
            study_title="DPDP Compliance Study",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid=f"SUBJ-{uuid.uuid4().hex[:6].upper()}",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()
        await db_session.refresh(patient)

        ecrf_resp_1 = await client.post(
            f"/api/v1/patients/{patient.id}/ecrf",
            json={
                "visit_number": 1,
                "visit_name": "Day 0",
                "form_data": {"systolic_bp": 120},
                "modified_by": "dr_vaidya",
            },
        )
        assert ecrf_resp_1.status_code == 201

        revoke_resp = await client.post(f"/api/v1/patients/{patient.id}/consent/revoke")
        assert revoke_resp.status_code == 200
        revoke_data = revoke_resp.json()
        assert revoke_data["consent_status"] == "WITHDRAWN"

        ecrf_resp_2 = await client.post(
            f"/api/v1/patients/{patient.id}/ecrf",
            json={
                "visit_number": 2,
                "visit_name": "Day 14",
                "form_data": {"systolic_bp": 118},
                "modified_by": "dr_vaidya",
            },
        )
        assert ecrf_resp_2.status_code == 400
        assert "withdrawn consent" in ecrf_resp_2.json()["detail"]

        audit_stmt = (
            select(AlcoaAuditLedger)
            .where(
                AlcoaAuditLedger.entity_name == "trial_patients",
                AlcoaAuditLedger.entity_id == str(patient.id),
            )
            .order_by(AlcoaAuditLedger.sequence_id.desc())
        )
        audit_res = await db_session.execute(audit_stmt)
        latest_audit = audit_res.scalars().first()
        assert latest_audit is not None
        assert latest_audit.field_changes.get("dpdp_revocation") is True

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        assert verify_resp.json()["status"] == "VERIFIED_SECURE"


class TestMerkleWitnessNotarizationAndTamperDefense:

    def test_merkle_tree_math_deterministic(self):
        leaf_1 = "a" * 64
        leaf_2 = "b" * 64
        leaf_3 = "c" * 64

        root_empty = build_merkle_tree([])
        assert len(root_empty) == 64

        root_single = build_merkle_tree([leaf_1])
        assert root_single == leaf_1

        root_multi = build_merkle_tree([leaf_1, leaf_2, leaf_3])
        assert len(root_multi) == 64
        assert root_multi == build_merkle_tree([leaf_1, leaf_2, leaf_3])

    async def test_clean_ledger_notarization_verifies_secure(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-MERKLE-{uuid.uuid4().hex[:6].upper()}",
            study_title="Merkle Proof Study",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid=f"SUBJ-{uuid.uuid4().hex[:6].upper()}",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()
        await db_session.refresh(patient)

        await client.post(
            f"/api/v1/patients/{patient.id}/ecrf",
            json={
                "visit_number": 1,
                "visit_name": "Day 0",
                "form_data": {"systolic_bp": 120},
                "modified_by": "dr_vaidya",
            },
        )

        notarize_resp = await client.post("/api/v1/audit/notarize-witness")
        assert notarize_resp.status_code == 200
        notarized_root = notarize_resp.json()["merkle_root"]
        assert len(notarized_root) == 64

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["status"] == "VERIFIED_SECURE"
        assert verify_data["tamper_detected"] is False
        assert verify_data["local_merkle_root"] == notarized_root
        assert verify_data["witness_merkle_root"] == notarized_root

    async def test_recomputed_linear_hashes_caught_by_merkle_witness(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-FRAUD-{uuid.uuid4().hex[:6].upper()}",
            study_title="DBA Fraud Simulation Trial",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid=f"SUBJ-{uuid.uuid4().hex[:6].upper()}",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()
        await db_session.refresh(patient)

        for visit in [1, 2, 3]:
            await client.post(
                f"/api/v1/patients/{patient.id}/ecrf",
                json={
                    "visit_number": visit,
                    "visit_name": f"Day {visit * 7}",
                    "form_data": {"systolic_bp": 120 + visit},
                    "modified_by": "dr_vaidya",
                },
            )

        notarize_resp = await client.post("/api/v1/audit/notarize-witness")
        assert notarize_resp.status_code == 200
        witness_root = notarize_resp.json()["merkle_root"]

        stmt = select(AlcoaAuditLedger).order_by(AlcoaAuditLedger.sequence_id.asc())
        rows_res = await db_session.execute(stmt)
        blocks = list(rows_res.scalars().all())
        assert len(blocks) >= 3

        target_block = blocks[1]
        mutated_changes = dict(target_block.field_changes)
        mutated_changes["form_data"] = {"systolic_bp": 999, "fraud": True}

        prev = target_block.prev_hash
        new_hash = _compute_hash(
            prev_hash=prev,
            entity_id=target_block.entity_id,
            field_changes=mutated_changes,
            modified_by=target_block.modified_by,
            timestamp=target_block.timestamp,
        )

        await db_session.execute(
            text(
                "UPDATE alcoa_audit_ledger SET field_changes = :fc, current_hash = :ch WHERE sequence_id = :sid"
            ),
            {"fc": '{"systolic_bp": 999, "fraud": true}', "ch": new_hash, "sid": target_block.sequence_id},
        )

        current_prev = new_hash
        for b in blocks[2:]:
            recomputed = _compute_hash(
                prev_hash=current_prev,
                entity_id=b.entity_id,
                field_changes=b.field_changes,
                modified_by=b.modified_by,
                timestamp=b.timestamp,
            )
            await db_session.execute(
                text(
                    "UPDATE alcoa_audit_ledger SET prev_hash = :ph, current_hash = :ch WHERE sequence_id = :sid"
                ),
                {"ph": current_prev, "ch": recomputed, "sid": b.sequence_id},
            )
            current_prev = recomputed

        await db_session.commit()

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()

        assert verify_data["status"] == "TAMPER_DETECTED"
        assert verify_data["reason"] == "WITNESS_ROOT_MISMATCH"
        assert verify_data["tamper_detected"] is True
        assert verify_data["local_merkle_root"] != witness_root
        assert verify_data["witness_merkle_root"] == witness_root
