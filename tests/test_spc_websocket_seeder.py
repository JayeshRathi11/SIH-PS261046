import uuid
from datetime import datetime, timedelta, timezone
import pytest
import httpx
from starlette.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.clinical import (
    AdverseEvent,
    AESeverity,
    AEStatus,
    ClinicalTrial,
    ConsentStatus,
    ECRFRecord,
    TrialPatient,
    TrialSite,
    TrialStatus,
)
from app.services.spc_engine import (
    calculate_mean_and_stdev,
    compute_z_score,
    is_spc_anomaly,
)


@pytest.mark.asyncio
class TestStatisticalProcessControlEngine:

    async def test_spc_math_helpers(self):
        m, s = calculate_mean_and_stdev([14.0, 14.0, 14.0, 14.0])
        assert m == 14.0
        assert s == 0.0

        m2, s2 = calculate_mean_and_stdev([10.0, 20.0])
        assert m2 == 15.0
        assert round(s2, 2) == 7.07

        z_normal = compute_z_score(15.0, 15.0, 5.0)
        assert z_normal == 0.0
        assert is_spc_anomaly(z_normal) is False

        z_anomaly = compute_z_score(30.0, 15.0, 5.0)
        assert z_anomaly == 3.0
        assert is_spc_anomaly(z_anomaly) is True

    async def test_spc_flags_protocol_drift_anomaly_over_threshold(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        site = TrialSite(
            site_code=f"SPC-SITE-{uuid.uuid4().hex[:4].upper()}",
            site_name="SPC Test Hospital",
            city="New Delhi",
            is_active=True,
        )
        trial = ClinicalTrial(
            protocol_id=f"AIIA-SPC-{uuid.uuid4().hex[:6].upper()}",
            study_title="SPC Protocol Drift Evaluation",
            status=TrialStatus.RECRUITING,
        )
        db_session.add_all([site, trial])
        await db_session.flush()

        normal_patients = []
        for i in range(1, 6):
            p = TrialPatient(
                trial_id=trial.id,
                site_id=site.id,
                usubjid=f"USJ-SPC-NORM-{i}",
                prakriti_type="PITTA",
                baseline_agni="SAMA",
                consent_status=ConsentStatus.OBTAINED,
            )
            db_session.add(p)
            normal_patients.append(p)
        await db_session.flush()

        for p in normal_patients:
            r1 = ECRFRecord(
                patient_id=p.id,
                trial_id=trial.id,
                site_id=site.id,
                visit_number=1,
                visit_name="Visit 1",
                form_data={"interval_days": 0.0, "dosage_compliance_pct": 98.0},
            )
            r2 = ECRFRecord(
                patient_id=p.id,
                trial_id=trial.id,
                site_id=site.id,
                visit_number=2,
                visit_name="Visit 2",
                form_data={"interval_days": 14.0, "dosage_compliance_pct": 97.0},
            )
            db_session.add_all([r1, r2])

        p_drift = TrialPatient(
            trial_id=trial.id,
            site_id=site.id,
            usubjid="USJ-SPC-DRIFT-099",
            prakriti_type="VATA",
            baseline_agni="MANDA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(p_drift)
        await db_session.flush()

        r_drift_v1 = ECRFRecord(
            patient_id=p_drift.id,
            trial_id=trial.id,
            site_id=site.id,
            visit_number=1,
            visit_name="Visit 1",
            form_data={"interval_days": 0.0, "dosage_compliance_pct": 98.0},
        )
        r_drift_v2 = ECRFRecord(
            patient_id=p_drift.id,
            trial_id=trial.id,
            site_id=site.id,
            visit_number=2,
            visit_name="Visit 2",
            form_data={"interval_days": 48.0, "dosage_compliance_pct": 96.0},
        )
        db_session.add_all([r_drift_v1, r_drift_v2])
        await db_session.commit()

        res = await client.get(f"/api/v1/analytics/protocol-deviations/{trial.id}")
        assert res.status_code == 200
        data = res.json()

        assert "sites_baselines" in data
        assert str(site.id) in data["sites_baselines"]
        site_stats = data["sites_baselines"][str(site.id)]
        assert site_stats["total_records"] >= 12

        assert len(data["anomalies"]) > 0
        drift_anomaly = next(
            (a for a in data["anomalies"] if a["usubjid"] == "USJ-SPC-DRIFT-099"), None
        )
        assert drift_anomaly is not None
        assert drift_anomaly["anomaly_flag"] == "PROTOCOL_DRIFT_ANOMALY"
        assert drift_anomaly["metric"] == "VISIT_INTERVAL"
        assert drift_anomaly["z_score"] > 2.5

        assert any(p["usubjid"] == "USJ-SPC-DRIFT-099" for p in data["flagged_patients"])


def test_websocket_heartbeat_when_no_active_sae():
    with TestClient(app) as test_client:
        with test_client.websocket_connect("/ws/sla-countdown") as ws:
            frame = ws.receive_json()
            assert "type" in frame or "ae_id" in frame
            if "type" in frame:
                assert frame["type"] == "HEARTBEAT"
                assert frame["message"] == "NO_ACTIVE_SAE_COUNTDOWN"


@pytest.mark.asyncio
class TestWebSocketSlaCountdownTicker:

    async def test_websocket_pushes_active_sae_countdown_telemetry(
        self, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-WS-{uuid.uuid4().hex[:6].upper()}",
            study_title="WebSocket SAE Countdown Trial",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-WS-TICKER-01",
            prakriti_type="PITTA",
            baseline_agni="TIKSHNA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.flush()

        now = datetime.now(tz=timezone.utc)
        sae = AdverseEvent(
            patient_id=patient.id,
            severity=AESeverity.LIFE_THREATENING,
            is_serious=True,
            sae_clock_start=now,
            sla_deadline=now + timedelta(hours=24),
            status=AEStatus.OPEN,
            reported_by="dr_websocket_test",
            recorded_at=now,
        )
        db_session.add(sae)
        await db_session.commit()

        with TestClient(app) as test_client:
            with test_client.websocket_connect("/ws/sla-countdown") as ws:
                frame = ws.receive_json()
                assert frame["ae_id"] == str(sae.id)
                assert frame["patient_usubjid"] == "USJ-WS-TICKER-01"
                assert frame["sla_status"] == "CRITICAL_WINDOW_ACTIVE"
                assert 0 < frame["remaining_seconds"] <= 86400
                assert frame["threshold_alert"] in ("T-24h", "T-12h", "T-4h")


@pytest.mark.asyncio
class TestPitchReadyCohortAndDemoSeeder:

    async def test_seed_demo_data_endpoint_creates_cohort_and_demo_patient(
        self, client: httpx.AsyncClient
    ):
        res = await client.post("/api/v1/admin/seed-demo-data")
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SEEDED_SUCCESS"
        assert data["protocol_id"] == "AIIA-GUD-2026"
        assert data["site_01"] == "SITE-01"
        assert data["site_02"] == "SITE-02"
        assert data["demo_subject"] == "AIIA-P089"

        trials_res = await client.get("/api/v1/trials")
        assert trials_res.status_code == 200
        trials = trials_res.json()
        assert any(t["protocol_id"] == "AIIA-GUD-2026" for t in trials)

        patients_res = await client.get(
            "/api/v1/patients",
            headers={"X-User-Role": "SUPER_ADMIN"},
        )
        assert patients_res.status_code == 200
        patients = patients_res.json()
        assert any(p["usubjid"] == "AIIA-P089" for p in patients)
        assert len(patients) >= 21

    async def test_seeded_data_maintains_alcoa_ledger_validity(
        self, client: httpx.AsyncClient
    ):
        res_seed = await client.post("/api/v1/admin/seed-demo-data")
        assert res_seed.status_code == 201

        verify_res = await client.get("/api/v1/audit/verify-chain")
        assert verify_res.status_code == 200
        verify_data = verify_res.json()
        assert verify_data["status"] == "VERIFIED_SECURE"
        assert verify_data["tamper_detected"] is False
        assert verify_data["total_blocks"] > 0

    async def test_demo_patient_p089_ready_for_adverse_event_escalation(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        await client.post("/api/v1/admin/seed-demo-data")

        stmt = select(TrialPatient).where(TrialPatient.usubjid == "AIIA-P089")
        res = await db_session.execute(stmt)
        p089 = res.scalar_one()

        sae_payload = {
            "patient_id": str(p089.id),
            "severity": "HOSPITALIZATION",
            "clinical_notes": "Subject developed severe scleral icterus (netra-peetata) and vomiting (chhardi) with elevated ALT/AST transaminases",
            "ayurvedic_intervention": "Guduchi Extract 500mg BD",
            "concomitant_drugs": ["Aspirin 75mg OD"],
            "reported_by": "dr_apex_investigator",
        }
        create_sae_res = await client.post("/api/v1/safety/adverse-event", json=sae_payload)
        assert create_sae_res.status_code == 201
        sae_data = create_sae_res.json()

        assert sae_data["is_serious"] is True
        assert sae_data["has_conflict"] is True
        assert any("Guduchi" in c.get("herb", "") for c in sae_data["herb_drug_conflicts"])
        assert len(sae_data["coded_meddra_terms"]) > 0
        assert sae_data["form_ct16_available"] is True
        assert sae_data["sla_deadline"] is not None

        ct16_res = await client.get(f"/api/v1/safety/reports/ct16/{sae_data['id']}")
        assert ct16_res.status_code == 200
        assert ct16_res.headers["content-type"] == "application/pdf"
        assert ct16_res.content.startswith(b"%PDF-")
