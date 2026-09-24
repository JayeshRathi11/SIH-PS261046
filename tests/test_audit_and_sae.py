"""
AyuTrial-CTMS – Comprehensive Test Suite: Task 1
=================================================
Tests for ALCOA+ Cryptographic Audit Ledger & 24-Hour SAE State Machine.

Architecture for Python 3.14 + pytest-asyncio 1.4.0 + asyncpg:
  - asyncio_mode = auto (in pytest.ini)
  - asyncio_default_fixture_loop_scope = session (in pytest.ini)
  - All async fixtures and tests run in one shared session event loop.
  - test_engine is created inside a session-scoped fixture (not module level).
  - Tables created once per session, truncated before each test.
"""
import hashlib
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Optional

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import create_app
from app.models.clinical import (
    AESeverity,
    AlcoaAuditLedger,
    ClinicalTrial,
    TrialPatient,
    TrialStatus,
    ConsentStatus,
)

settings = get_settings()


# ---------------------------------------------------------------------------
# Session-scoped engine fixture (must be created inside async fixture, not
# at module level, to bind to the session event loop)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create one async engine for the entire test session."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

    # Create all tables once
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Teardown: drop tables and dispose engine
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def session_factory(test_engine: AsyncEngine) -> async_sessionmaker:
    """Session factory bound to the test engine."""
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# ---------------------------------------------------------------------------
# Per-test fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def clean_tables(test_engine: AsyncEngine):
    """Truncate all data before each test for isolation."""
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE alcoa_audit_ledger RESTART IDENTITY CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE adverse_events CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE trial_patients CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE clinical_trials CASCADE;"))
    yield


@pytest_asyncio.fixture
async def db_session(session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    """Per-test database session."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    """FastAPI test client with DB dependency overridden to test session."""
    app = create_app()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------
async def seed_trial_and_patient(db: AsyncSession) -> tuple:
    """Insert one trial and one enrolled patient, return both ORM objects."""
    trial = ClinicalTrial(
        protocol_id=f"AIIA-TEST-{uuid.uuid4().hex[:8].upper()}",
        study_title="Test Guduchi Safety Trial",
        status=TrialStatus.RECRUITING,
    )
    db.add(trial)
    await db.flush()

    patient = TrialPatient(
        trial_id=trial.id,
        usubjid=f"USJ-{uuid.uuid4().hex[:6].upper()}",
        prakriti_type="PITTA",
        baseline_agni="VISHAMA",
        consent_status=ConsentStatus.OBTAINED,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(trial)
    await db.refresh(patient)
    return trial, patient


# ===========================================================================
# TEST GROUP A: Normal AE vs SAE Escalation + 24-hour SLA
# ===========================================================================
class TestAdverseEventCreation:

    async def test_mild_ae_does_not_trigger_sae(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """MILD adverse event must NOT set is_serious, sae_clock_start, or sla_deadline."""
        _, patient = await seed_trial_and_patient(db_session)

        resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "MILD",
                "clinical_notes": "Slight headache after dose.",
                "reported_by": "dr_sharma",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()

        assert data["is_serious"] is False
        assert data["sae_clock_start"] is None
        assert data["sla_deadline"] is None
        assert data["severity"] == "MILD"
        assert data["status"] == "OPEN"

    async def test_moderate_ae_does_not_trigger_sae(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """MODERATE is not in SAE_SEVERITIES – no SAE flag."""
        _, patient = await seed_trial_and_patient(db_session)

        resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "MODERATE",
                "clinical_notes": "Nausea and mild vomiting.",
                "reported_by": "dr_patel",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_serious"] is False
        assert data["sae_clock_start"] is None

    @pytest.mark.parametrize("severity", ["HOSPITALIZATION", "LIFE_THREATENING", "DEATH"])
    async def test_sae_severities_trigger_24h_clock(
        self, severity: str, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """
        All three SAE severities must set is_serious=True and
        sla_deadline exactly 24 hours after sae_clock_start.
        """
        _, patient = await seed_trial_and_patient(db_session)

        before_call = datetime.now(tz=timezone.utc)

        resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": severity,
                "clinical_notes": f"Critical event: {severity}",
                "reported_by": "dr_rao",
            },
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()

        after_call = datetime.now(tz=timezone.utc)

        assert data["is_serious"] is True, f"Expected is_serious=True for severity={severity}"
        assert data["sae_clock_start"] is not None
        assert data["sla_deadline"] is not None

        clock_start = datetime.fromisoformat(data["sae_clock_start"])
        sla = datetime.fromisoformat(data["sla_deadline"])

        assert before_call <= clock_start <= after_call, (
            f"sae_clock_start {clock_start} not within [{before_call}, {after_call}]"
        )

        expected_sla = clock_start + timedelta(hours=24)
        delta = abs((sla - expected_sla).total_seconds())
        assert delta < 1.0, (
            f"SLA deadline {sla} should be exactly 24h after clock start {clock_start}. "
            f"Delta: {delta}s"
        )

    async def test_unknown_patient_returns_404(self, client: httpx.AsyncClient):
        """A patient_id that doesn't exist must return HTTP 404."""
        resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(uuid.uuid4()),
                "severity": "MILD",
                "clinical_notes": "Test note.",
                "reported_by": "dr_ghost",
            },
        )
        assert resp.status_code == 404


# ===========================================================================
# TEST GROUP B: ALCOA+ Chain Verification – VERIFIED_SECURE
# ===========================================================================
class TestAuditChainVerification:

    async def test_empty_ledger_is_verified_secure(self, client: httpx.AsyncClient):
        """Empty ledger must return VERIFIED_SECURE with 0 blocks."""
        resp = await client.get("/api/v1/audit/verify-chain")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "VERIFIED_SECURE"
        assert data["total_blocks"] == 0
        assert data["tampered_sequence_ids"] == []

    async def test_single_sae_produces_verified_chain(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """After logging one SAE, the chain must verify as VERIFIED_SECURE with 1 block."""
        _, patient = await seed_trial_and_patient(db_session)

        ae_resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "HOSPITALIZATION",
                "clinical_notes": "Acute liver toxicity – ICU admission.",
                "reported_by": "dr_aiia_coordinator",
            },
        )
        assert ae_resp.status_code == 201

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        data = verify_resp.json()
        assert data["status"] == "VERIFIED_SECURE"
        assert data["total_blocks"] == 1
        assert data["tampered_sequence_ids"] == []

    async def test_multiple_events_chain_is_verified_secure(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """Multiple sequential AE submissions must produce a fully intact chain."""
        _, patient = await seed_trial_and_patient(db_session)

        severities = ["MILD", "MODERATE", "HOSPITALIZATION", "MILD", "LIFE_THREATENING"]
        for sev in severities:
            r = await client.post(
                "/api/v1/safety/adverse-event",
                json={
                    "patient_id": str(patient.id),
                    "severity": sev,
                    "clinical_notes": f"Event of severity {sev}",
                    "reported_by": "dr_multi_test",
                },
            )
            assert r.status_code == 201

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        data = verify_resp.json()
        assert data["status"] == "VERIFIED_SECURE"
        assert data["total_blocks"] == len(severities)
        assert data["tampered_sequence_ids"] == []

    async def test_genesis_hash_is_prev_hash_of_first_block(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """The first block's prev_hash must equal GENESIS_BLOCK_HASH_AIIA_CTMS_2026."""
        from sqlalchemy import select as sa_select
        _, patient = await seed_trial_and_patient(db_session)

        await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "MILD",
                "clinical_notes": "Genesis block test.",
                "reported_by": "system",
            },
        )

        stmt = sa_select(AlcoaAuditLedger).order_by(AlcoaAuditLedger.sequence_id.asc()).limit(1)
        result = await db_session.execute(stmt)
        first_block = result.scalar_one()

        assert first_block.prev_hash == settings.GENESIS_HASH


# ===========================================================================
# TEST GROUP C: Intentional Tamper Detection
# ===========================================================================
class TestTamperDetection:

    async def test_tamper_detected_after_raw_sql_mutation(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """
        DBA fraud simulation: raw SQL mutates block #1's field_changes.
        Expected: verify-chain returns TAMPER_DETECTED with sequence_id=1.
        """
        _, patient = await seed_trial_and_patient(db_session)

        # Step 1: Create two audit blocks
        for sev in ["HOSPITALIZATION", "MILD"]:
            r = await client.post(
                "/api/v1/safety/adverse-event",
                json={
                    "patient_id": str(patient.id),
                    "severity": sev,
                    "clinical_notes": f"AE with severity {sev}",
                    "reported_by": "dr_fraud_test",
                },
            )
            assert r.status_code == 201

        # Step 2: Confirm chain is intact
        pre_verify = await client.get("/api/v1/audit/verify-chain")
        assert pre_verify.json()["status"] == "VERIFIED_SECURE"
        assert pre_verify.json()["total_blocks"] == 2

        # Step 3: Raw SQL tamper – mutate block #1's field_changes
        tampered_payload = json.dumps({"severity": "MILD", "is_serious": False})
        await db_session.execute(
            text(
                "UPDATE alcoa_audit_ledger "
                "SET field_changes = :payload "
                "WHERE sequence_id = 1"
            ),
            {"payload": tampered_payload},
        )
        await db_session.commit()

        # Step 4: Re-run verify-chain
        post_verify = await client.get("/api/v1/audit/verify-chain")
        post_data = post_verify.json()

        # Step 5: Assert tamper detected
        assert post_data["status"] == "TAMPER_DETECTED", (
            f"Expected TAMPER_DETECTED but got: {post_data}"
        )
        assert 1 in post_data["tampered_sequence_ids"], (
            f"Expected sequence_id=1 in tampered list, got: {post_data['tampered_sequence_ids']}"
        )

    async def test_tamper_in_middle_of_chain_cascades(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """
        Tampering block #2 breaks its hash AND subsequent blocks' prev_hash linkage.
        """
        _, patient = await seed_trial_and_patient(db_session)

        for _ in range(4):
            r = await client.post(
                "/api/v1/safety/adverse-event",
                json={
                    "patient_id": str(patient.id),
                    "severity": "MILD",
                    "clinical_notes": "Cascade tamper test event.",
                    "reported_by": "dr_cascade",
                },
            )
            assert r.status_code == 201

        # Tamper block #2
        tampered_payload = json.dumps({"severity": "DEATH", "is_serious": True})
        await db_session.execute(
            text(
                "UPDATE alcoa_audit_ledger "
                "SET field_changes = :payload "
                "WHERE sequence_id = 2"
            ),
            {"payload": tampered_payload},
        )
        await db_session.commit()

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        data = verify_resp.json()

        assert data["status"] == "TAMPER_DETECTED"
        assert 2 in data["tampered_sequence_ids"], (
            f"Block 2 should be tampered. Got: {data['tampered_sequence_ids']}"
        )

    async def test_current_hash_mutation_detected(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        """
        Attacker changes both field_changes AND current_hash – next block's
        prev_hash still breaks, triggering tamper detection.
        """
        _, patient = await seed_trial_and_patient(db_session)

        for _ in range(3):
            r = await client.post(
                "/api/v1/safety/adverse-event",
                json={
                    "patient_id": str(patient.id),
                    "severity": "MILD",
                    "clinical_notes": "Hash mutation test.",
                    "reported_by": "dr_hash_attacker",
                },
            )
            assert r.status_code == 201

        fake_hash = hashlib.sha256(b"forged_data").hexdigest()
        await db_session.execute(
            text(
                "UPDATE alcoa_audit_ledger "
                "SET field_changes = '{\"severity\": \"MILD\"}'::jsonb, "
                "    current_hash = :fake_hash "
                "WHERE sequence_id = 1"
            ),
            {"fake_hash": fake_hash},
        )
        await db_session.commit()

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        data = verify_resp.json()

        assert data["status"] == "TAMPER_DETECTED"
        assert len(data["tampered_sequence_ids"]) >= 1
