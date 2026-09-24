import uuid
from datetime import datetime, timedelta, timezone
import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.clinical import (
    ClinicalTrial,
    ConsentStatus,
    TrialPatient,
    TrialStatus,
)
from app.services.watchdog import (
    record_daemon_heartbeat,
    set_daemon_heartbeat_time,
)


@pytest.mark.asyncio
class TestSemanticCaseSimilaritySearch:

    async def test_semantic_search_finds_p089_on_hepatic_query(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        await client.post("/api/v1/admin/seed-demo-data")

        stmt = select(TrialPatient).where(TrialPatient.usubjid == "AIIA-P089")
        res = await db_session.execute(stmt)
        p089 = res.scalar_one()

        sae_payload = {
            "patient_id": str(p089.id),
            "severity": "HOSPITALIZATION",
            "clinical_notes": "Subject developed severe scleral icterus (netra-peetata) and vomiting (chhardi) with elevated ALT/AST transaminases and jaundice",
            "ayurvedic_intervention": "Guduchi Extract 500mg BD",
            "concomitant_drugs": ["Aspirin 75mg OD"],
            "reported_by": "dr_apex_investigator",
        }
        create_sae = await client.post("/api/v1/safety/adverse-event", json=sae_payload)
        assert create_sae.status_code == 201

        search_res = await client.get(
            "/api/v1/safety/cases/similar?query=hepatic+tenderness+and+peeli+aankhein"
        )
        assert search_res.status_code == 200
        results = search_res.json()
        assert len(results) > 0

        top_match = results[0]
        assert top_match["usubjid"] == "AIIA-P089"
        assert top_match["similarity_score"] > 0.45
        assert top_match["similarity_percentage"] > 45.0
        assert "scleral icterus" in top_match["clinical_notes"]

    async def test_unrelated_query_returns_no_matches_above_threshold(
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
        await client.post("/api/v1/safety/adverse-event", json=sae_payload)

        unrelated_res = await client.get(
            "/api/v1/safety/cases/similar?query=mild+dry+skin+rash&threshold=0.30"
        )
        assert unrelated_res.status_code == 200
        unrelated_results = unrelated_res.json()
        assert len(unrelated_results) == 0


@pytest.mark.asyncio
class TestRegulatoryIdempotencyShield:

    async def test_idempotency_key_blocks_duplicate_submission(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id=f"AIIA-IDEMP-{uuid.uuid4().hex[:6].upper()}",
            study_title="Idempotency Shield Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-IDEMP-001",
            prakriti_type="PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()

        ae_payload = {
            "patient_id": str(patient.id),
            "severity": "MILD",
            "clinical_notes": "Mild nausea without vomiting",
            "ayurvedic_intervention": "Brahmi Vati",
            "concomitant_drugs": [],
            "reported_by": "dr_idemp_tester",
        }

        headers = {"X-Idempotency-Key": "IDEMP-TX-101"}

        res1 = await client.post("/api/v1/safety/adverse-event", json=ae_payload, headers=headers)
        assert res1.status_code == 201
        data1 = res1.json()
        assert data1["patient_id"] == str(patient.id)

        res2 = await client.post("/api/v1/safety/adverse-event", json=ae_payload, headers=headers)
        assert res2.status_code == 409
        data2 = res2.json()
        assert "Duplicate transaction detected" in data2["detail"]
        assert data2["idempotency_key"] == "IDEMP-TX-101"

        headers_diff = {"X-Idempotency-Key": "IDEMP-TX-102"}
        res3 = await client.post("/api/v1/safety/adverse-event", json=ae_payload, headers=headers_diff)
        assert res3.status_code == 201


@pytest.mark.asyncio
class TestDeadMansSwitchWatchdog:

    async def test_watchdog_returns_healthy_when_heartbeat_is_fresh(
        self, client: httpx.AsyncClient
    ):
        record_daemon_heartbeat()

        res = await client.get("/api/v1/health/sae-daemon?max_staleness=30")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "HEALTHY"
        assert data["is_healthy"] is True
        assert data["staleness_seconds"] < 5

    async def test_watchdog_returns_503_when_heartbeat_stalled(
        self, client: httpx.AsyncClient
    ):
        stalled_time = datetime.now(tz=timezone.utc) - timedelta(seconds=45)
        set_daemon_heartbeat_time(stalled_time)

        res = await client.get("/api/v1/health/sae-daemon?max_staleness=30")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "DEGRADED_STALE_DAEMON"
        assert data["is_healthy"] is False
        assert data["staleness_seconds"] >= 44
        assert "unacknowledged_saes" in data

    async def test_watchdog_returns_503_when_no_heartbeat_recorded(
        self, client: httpx.AsyncClient
    ):
        set_daemon_heartbeat_time(None)

        res = await client.get("/api/v1/health/sae-daemon")
        assert res.status_code == 503
        data = res.json()
        assert data["status"] == "DEGRADED_STALE_DAEMON"
        assert data["is_healthy"] is False
        assert "not recorded" in data["message"]
