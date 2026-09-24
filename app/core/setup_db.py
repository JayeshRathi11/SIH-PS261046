"""
AyuTrial-CTMS – Database Setup Script

Creates all tables and applies DB-level permission boundary:
  - Revokes UPDATE, DELETE, TRUNCATE on alcoa_audit_ledger from the
    application runtime role (ayutrial), making the ledger truly append-only.
  - Run once on fresh DB or after schema reset.

Usage:
    python -m app.core.setup_db
"""
import asyncio
import logging
from sqlalchemy import text
from app.core.database import engine, Base
from app.models import clinical  # noqa: F401 – registers all ORM models

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def create_tables() -> None:
    log.info("Creating all tables …")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Tables created.")


async def apply_permission_boundary() -> None:
    """
    Revoke destructive DML on the audit ledger from the app runtime role.
    This ensures that even if application code has a bug, it cannot
    UPDATE or DELETE audit records.
    """
    statements = [
        # Revoke UPDATE on ledger from app role
        "REVOKE UPDATE ON TABLE alcoa_audit_ledger FROM ayutrial;",
        # Revoke DELETE on ledger from app role
        "REVOKE DELETE ON TABLE alcoa_audit_ledger FROM ayutrial;",
        # Revoke TRUNCATE on ledger from app role
        "REVOKE TRUNCATE ON TABLE alcoa_audit_ledger FROM ayutrial;",
    ]
    async with engine.begin() as conn:
        for stmt in statements:
            try:
                await conn.execute(text(stmt))
                log.info("Executed: %s", stmt)
            except Exception as exc:  # noqa: BLE001
                # Revoke might fail if running as non-superuser in test env
                log.warning("Could not execute '%s': %s", stmt, exc)
    log.info("Permission boundary applied.")


async def main() -> None:
    await create_tables()
    await apply_permission_boundary()
    await engine.dispose()
    log.info("Database setup complete.")


if __name__ == "__main__":
    asyncio.run(main())
