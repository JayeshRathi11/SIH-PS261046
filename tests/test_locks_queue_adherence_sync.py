import asyncio
import time
import uuid
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AlcoaAuditLedger,
    ClinicalTrial,
    ConsentStatus,
    DeadLetterExport,
    ECRFRecord,
    PatientAdherenceLog,
    TrialPatient,
    TrialStatus,
)
from app.services.export_queue import process_export_with_dead_letter_isolation
from app.services.lock_manager import lock_manager


async def seed_test_context(db: AsyncSession) -> tuple[ClinicalTrial, TrialPatient]:
    trial = ClinicalTrial(
        protocol_id=f"AIIA-LOCK-{uuid.uuid4().hex[:6].upper()}",
        study_title="Task 8 Lock and Sync Verification Protocol",
        status=TrialStatus.RECRUITING,
    )
    db.add(trial)
    await db.flush()

    patient = TrialPatient(
        trial_id=trial.id,
        usubjid=f"USJ-{uuid.uuid4().hex[:6].upper()}",
        prakriti_type="PITTA",
        baseline_agni="SAMA",
        consent_status=ConsentStatus.OBTAINED,
        telegram_chat_id="tg_user_998877",
    )
    db.add(patient)
    await db.commit()
    await db.refresh(trial)
    await db.refresh(patient)
    return trial, patient


# ===========================================================================
# GROUP A: Real-Time Field-Level Concurrency Locking
# ===========================================================================
class TestFieldConcurrencyLocking:

    async def test_acquire_and_contention_lock(self, client: httpx.AsyncClient):
        rec_id = str(uuid.uuid4())
        field = "systolic_bp"

        # User A acquires lock
        resp1 = await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": rec_id,
                "field_name": field,
                "user_id": "dr_vaidya",
                "ttl_seconds": 30,
            },
        )
        assert resp1.status_code == 200
        assert resp1.json()["status"] == "ACQUIRED"
        assert resp1.json()["user_id"] == "dr_vaidya"

        # User B attempts to acquire same field -> HTTP 423 Locked
        resp2 = await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": rec_id,
                "field_name": field,
                "user_id": "coord_sharma",
                "ttl_seconds": 30,
            },
        )
        assert resp2.status_code == 423
        body2 = resp2.json()
        assert "locked" in body2["detail"]["message"].lower()
        assert body2["detail"]["lock_holder"] == "dr_vaidya"

    async def test_release_and_reacquire(self, client: httpx.AsyncClient):
        rec_id = str(uuid.uuid4())
        field = "diastolic_bp"

        # User A acquires
        await client.post(
            "/api/v1/locks/acquire",
            json={"record_id": rec_id, "field_name": field, "user_id": "dr_vaidya"},
        )

        # User A releases
        rel_resp = await client.post(
            "/api/v1/locks/release",
            json={"record_id": rec_id, "field_name": field, "user_id": "dr_vaidya"},
        )
        assert rel_resp.status_code == 200
        assert rel_resp.json()["status"] == "RELEASED"

        # User B acquires successfully now
        acq_resp = await client.post(
            "/api/v1/locks/acquire",
            json={"record_id": rec_id, "field_name": field, "user_id": "coord_sharma"},
        )
        assert acq_resp.status_code == 200
        assert acq_resp.json()["user_id"] == "coord_sharma"

    async def test_unauthorized_release_forbidden(self, client: httpx.AsyncClient):
        rec_id = str(uuid.uuid4())
        field = "heart_rate"

        # User A acquires
        await client.post(
            "/api/v1/locks/acquire",
            json={"record_id": rec_id, "field_name": field, "user_id": "dr_vaidya"},
        )

        # User B tries to release User A's lock
        rel_resp = await client.post(
            "/api/v1/locks/release",
            json={"record_id": rec_id, "field_name": field, "user_id": "coord_sharma"},
        )
        assert rel_resp.status_code == 403

    async def test_expired_lock_auto_freed(self, client: httpx.AsyncClient):
        rec_id = str(uuid.uuid4())
        field = "alt_enzyme"

        # Acquire with 1s TTL
        await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": rec_id,
                "field_name": field,
                "user_id": "dr_vaidya",
                "ttl_seconds": 1,
            },
        )

        # Wait for expiration
        await asyncio.sleep(1.1)

        # User B can now acquire without 423
        resp2 = await client.post(
            "/api/v1/locks/acquire",
            json={
                "record_id": rec_id,
                "field_name": field,
                "user_id": "coord_sharma",
                "ttl_seconds": 30,
            },
        )
        assert resp2.status_code == 200
        assert resp2.json()["user_id"] == "coord_sharma"

    async def test_get_active_locks(self, client: httpx.AsyncClient):
        rec_id = str(uuid.uuid4())

        await client.post(
            "/api/v1/locks/acquire",
            json={"record_id": rec_id, "field_name": "temp", "user_id": "user1"},
        )
        await client.post(
            "/api/v1/locks/acquire",
            json={"record_id": rec_id, "field_name": "pulse", "user_id": "user2"},
        )

        resp = await client.get(f"/api/v1/locks/{rec_id}")
        assert resp.status_code == 200
        active = resp.json()["active_locks"]
        assert "temp" in active
        assert "pulse" in active
        assert active["temp"]["user_id"] == "user1"
        assert active["pulse"]["user_id"] == "user2"


# ===========================================================================
# GROUP B: Self-Healing Dead-Letter Export Retry Queue
# ===========================================================================
class TestDeadLetterExportQueue:

    async def test_dead_letter_isolation_on_batch_export(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, _ = await seed_test_context(db_session)

        records = [
            {"usubjid": "PAT-001", "domain": "DM", "age": 45, "sex": "M"},
            {"usubjid": "", "domain": "DM", "_is_corrupt": True, "error": "Corrupted memory buffer"},
            {"usubjid": "PAT-002", "domain": "DM", "age": 52, "sex": "F"},
        ]

        result = await process_export_with_dead_letter_isolation(
            trial_id=trial.id,
            records=records,
            export_type="CDISC_SDTM",
            db=db_session,
        )

        assert result["status"] == "COMPLETED_WITH_ISOLATIONS"
        assert result["total_records"] == 3
        assert result["successful_count"] == 2
        assert result["quarantined_count"] == 1

        # Check DB model dead_letter_exports
        stmt = select(DeadLetterExport).where(DeadLetterExport.trial_id == trial.id)
        res = await db_session.execute(stmt)
        quarantined = res.scalars().all()
        assert len(quarantined) == 1
        assert quarantined[0].status == "ISOLATED"
        assert "Malformed record payload" in quarantined[0].error_trace

    async def test_dead_letter_endpoint_lists_quarantined(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, _ = await seed_test_context(db_session)

        # Add quarantined item
        corrupt = [
            {"record_identifier": "CORRUPT-XYZ", "_is_corrupt": True, "syntax": "{invalid_json"}
        ]
        await process_export_with_dead_letter_isolation(
            trial_id=trial.id,
            records=corrupt,
            export_type="HL7_FHIR",
            db=db_session,
        )

        resp = await client.get(f"/api/v1/export/dead-letter/{trial.id}")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) >= 1
        assert items[0]["export_type"] == "HL7_FHIR"
        assert items[0]["status"] == "ISOLATED"
        assert items[0]["record_identifier"] == "CORRUPT-XYZ"


# ===========================================================================
# GROUP C: Telegram-Based Adherence Webhook
# ===========================================================================
class TestTelegramAdherenceWebhook:

    async def test_telegram_webhook_callback_query_taken(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_test_context(db_session)

        # Telegram CallbackQuery for "Maine Dawa Li"
        webhook_payload = {
            "update_id": 9001,
            "callback_query": {
                "from": {"id": 998877, "username": "ayur_patient"},
                "data": "Maine Dawa Li",
            },
        }

        resp = await client.post(
            "/api/v1/adherence/telegram-webhook",
            json=webhook_payload,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "RECORDED"
        assert data["dosage_status"] == "TAKEN"
        assert data["patient_id"] == str(patient.id)

        # Verify adherence log in DB
        stmt_log = select(PatientAdherenceLog).where(PatientAdherenceLog.patient_id == patient.id)
        res_log = await db_session.execute(stmt_log)
        logs = res_log.scalars().all()
        assert len(logs) == 1
        assert logs[0].dosage_status == "TAKEN"
        assert logs[0].reported_via == "TELEGRAM_BOT"

        # Verify ALCOA+ Audit Ledger entry
        stmt_audit = select(AlcoaAuditLedger).where(
            AlcoaAuditLedger.entity_name == "patient_adherence_logs",
            AlcoaAuditLedger.entity_id == str(logs[0].id),
        )
        res_audit = await db_session.execute(stmt_audit)
        audit_entry = res_audit.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.modified_by == "telegram_bot"
        assert audit_entry.field_changes["dosage_status"] == "TAKEN"

        # Check compliance calculation API
        calc_resp = await client.get(f"/api/v1/adherence/{patient.id}")
        assert calc_resp.status_code == 200
        calc = calc_resp.json()
        assert calc["total_reported"] == 1
        assert calc["dosages_taken"] == 1
        assert calc["dosages_missed"] == 0
        assert calc["compliance_percentage"] == 100.0

    async def test_telegram_webhook_missed_dose_updates_compliance(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_test_context(db_session)

        # Dose 1: Taken
        await client.post(
            "/api/v1/adherence/telegram-webhook",
            json={"telegram_chat_id": "tg_user_998877", "dosage_status": "TAKEN"},
        )

        # Dose 2: Missed ("Miss Ho Gayi")
        await client.post(
            "/api/v1/adherence/telegram-webhook",
            json={"telegram_chat_id": "tg_user_998877", "dosage_status": "Miss Ho Gayi"},
        )

        # Check compliance calculation API
        calc_resp = await client.get(f"/api/v1/adherence/{patient.id}")
        assert calc_resp.status_code == 200
        calc = calc_resp.json()
        assert calc["total_reported"] == 2
        assert calc["dosages_taken"] == 1
        assert calc["dosages_missed"] == 1
        assert calc["compliance_percentage"] == 50.0

    async def test_telegram_webhook_unknown_patient_404(
        self, client: httpx.AsyncClient
    ):
        resp = await client.post(
            "/api/v1/adherence/telegram-webhook",
            json={"telegram_chat_id": "unknown_unregistered_id", "dosage_status": "TAKEN"},
        )
        assert resp.status_code == 404


# ===========================================================================
# GROUP D: Offline-First Conflict-Aware Batch Sync Engine
# ===========================================================================
class TestOfflineBatchSync:

    async def test_offline_batch_sync_clean_insert(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_test_context(db_session)

        client_time = datetime.now(timezone.utc).isoformat()
        mutations = [
            {
                "client_mutation_id": str(uuid.uuid4()),
                "patient_id": str(patient.id),
                "visit_number": 1,
                "visit_name": "Day 0 - Baseline Offline",
                "form_data": {"systolic_bp": 128, "diastolic_bp": 82, "heart_rate": 72},
                "client_timestamp": client_time,
            }
        ]

        resp = await client.post(
            "/api/v1/sync/offline-batch",
            json={
                "trial_id": str(trial.id),
                "mutations": mutations,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_mutations"] == 1
        assert data["inserted_count"] == 1
        assert data["results"][0]["status"] == "INSERTED_CLEAN"

        # Check DB
        stmt = select(ECRFRecord).where(
            ECRFRecord.patient_id == patient.id,
            ECRFRecord.visit_number == 1,
        )
        res = await db_session.execute(stmt)
        rec = res.scalar_one_or_none()
        assert rec is not None
        assert rec.form_data["systolic_bp"] == 128

        # Check ALCOA+ Audit
        stmt_audit = select(AlcoaAuditLedger).where(
            AlcoaAuditLedger.entity_name == "ecrf_records",
            AlcoaAuditLedger.entity_id == str(rec.id),
        )
        res_audit = await db_session.execute(stmt_audit)
        audit_entry = res_audit.scalar_one_or_none()
        assert audit_entry is not None
        assert audit_entry.modified_by == "offline_sync_client"

    async def test_offline_batch_sync_client_win_newer_timestamp(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_test_context(db_session)

        # Existing record on server at T0
        t0 = datetime.now(timezone.utc) - timedelta(hours=2)
        ecrf = ECRFRecord(
            patient_id=patient.id,
            trial_id=trial.id,
            visit_number=2,
            visit_name="Day 14 Followup",
            form_data={"systolic_bp": 130},
            recorded_at=t0,
            updated_at=t0,
        )
        db_session.add(ecrf)
        await db_session.commit()

        # Client sends offline update with newer timestamp T1 > T0
        t1 = datetime.now(timezone.utc)
        mutations = [
            {
                "client_mutation_id": "mut_client_win_01",
                "patient_id": str(patient.id),
                "visit_number": 2,
                "visit_name": "Day 14 Followup Updated",
                "form_data": {"systolic_bp": 120, "notes": "Patient improved"},
                "client_timestamp": t1.isoformat(),
            }
        ]

        resp = await client.post(
            "/api/v1/sync/offline-batch",
            json={
                "trial_id": str(trial.id),
                "mutations": mutations,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["client_win_count"] == 1
        assert data["results"][0]["status"] == "RESOLVED_CLIENT_WIN"

        # Check DB was updated with client winning form_data
        await db_session.refresh(ecrf)
        assert ecrf.form_data["systolic_bp"] == 120
        assert ecrf.form_data["notes"] == "Patient improved"

    async def test_offline_batch_sync_server_win_stale_timestamp(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_test_context(db_session)

        # Existing record on server at T_server (recent)
        t_server = datetime.now(timezone.utc)
        ecrf = ECRFRecord(
            patient_id=patient.id,
            trial_id=trial.id,
            visit_number=3,
            visit_name="Day 28 Visit",
            form_data={"systolic_bp": 118, "status": "VERIFIED_BY_INVESTIGATOR"},
            recorded_at=t_server,
            updated_at=t_server,
        )
        db_session.add(ecrf)
        await db_session.commit()

        # Client sends offline mutation with stale timestamp T_stale < T_server
        t_stale = t_server - timedelta(hours=3)
        mutations = [
            {
                "client_mutation_id": "mut_stale_01",
                "patient_id": str(patient.id),
                "visit_number": 3,
                "visit_name": "Day 28 Old Mutation",
                "form_data": {"systolic_bp": 140, "status": "OLD_DRAFT"},
                "client_timestamp": t_stale.isoformat(),
            }
        ]

        resp = await client.post(
            "/api/v1/sync/offline-batch",
            json={
                "trial_id": str(trial.id),
                "mutations": mutations,
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["server_win_count"] == 1
        assert data["results"][0]["status"] == "CONFLICT_SERVER_WIN"

        # Verify server state is uncorrupted / preserved
        await db_session.refresh(ecrf)
        assert ecrf.form_data["systolic_bp"] == 118
        assert ecrf.form_data["status"] == "VERIFIED_BY_INVESTIGATOR"
