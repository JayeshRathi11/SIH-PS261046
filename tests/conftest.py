import uuid
from typing import AsyncGenerator

import httpx
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
    ClinicalTrial,
    ConsentStatus,
    TrialPatient,
    TrialStatus,
)

settings = get_settings()


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE trial_patients ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR(100);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_trial_patients_telegram_chat_id ON trial_patients (telegram_chat_id);"))
    yield engine
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    except Exception:
        pass
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def session_factory(test_engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(test_engine: AsyncEngine):
    from app.services.merkle import set_notarized_root
    from app.services.analytics_service import invalidate_kpi_cache
    from app.core.idempotency import clear_idempotency_cache
    from app.services.watchdog import set_daemon_heartbeat_time
    from app.services.lock_manager import lock_manager
    set_notarized_root(None)
    invalidate_kpi_cache()
    clear_idempotency_cache()
    set_daemon_heartbeat_time(None)
    lock_manager.clear()
    async with test_engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE alcoa_audit_ledger RESTART IDENTITY CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE access_audit_logs CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE adverse_events CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE ecrf_records CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE dead_letter_exports CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE patient_adherence_logs CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE trial_patients CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE clinical_trials CASCADE;"))
        await conn.execute(text("TRUNCATE TABLE trial_sites CASCADE;"))
    yield
    set_notarized_root(None)
    invalidate_kpi_cache()
    clear_idempotency_cache()
    set_daemon_heartbeat_time(None)
    lock_manager.clear()


@pytest_asyncio.fixture
async def db_session(session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    app = create_app()

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac


async def seed_trial_and_patient(db: AsyncSession) -> tuple:
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
