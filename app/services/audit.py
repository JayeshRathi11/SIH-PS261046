"""
AyuTrial-CTMS – ALCOA+ Cryptographic Audit Chain Service

Implements SHA-256 hash chaining per the formula:
    CurrentHash = SHA256(PrevHash + EntityID + JSONDelta + UserID + Timestamp)

Genesis block links to the constant:
    GENESIS_BLOCK_HASH_AIIA_CTMS_2026

The audit ledger table is append-only; no UPDATE/DELETE is permitted on it
(enforced by DB-level permission revocation during setup).
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.clinical import AlcoaAuditLedger, AuditAction

settings = get_settings()


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------
def _compute_hash(
    prev_hash: str,
    entity_id: str,
    field_changes: dict[str, Any],
    modified_by: str,
    timestamp: datetime,
) -> str:
    """
    Deterministic SHA-256 hash for a single audit ledger block.
    JSON is serialized with sorted keys to guarantee determinism.
    """
    raw = (
        prev_hash
        + entity_id
        + json.dumps(field_changes, sort_keys=True, default=str)
        + modified_by
        + timestamp.isoformat()
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Public service: write a single audit entry
# ---------------------------------------------------------------------------
async def append_audit_entry(
    db: AsyncSession,
    *,
    entity_name: str,
    entity_id: str,
    action_type: AuditAction,
    field_changes: dict[str, Any],
    modified_by: str,
) -> AlcoaAuditLedger:
    """
    Append a new block to the ALCOA+ audit ledger atomically.

    Steps:
    1. Fetch the latest block's current_hash (prev_hash for new block).
    2. Compute new block hash.
    3. Insert the new ledger row.

    Must be called within an active transaction managed by the caller.
    """
    now = datetime.now(tz=timezone.utc)

    # --- Step 1: Fetch prev_hash -----------------------------------------
    stmt = (
        select(AlcoaAuditLedger.current_hash)
        .order_by(AlcoaAuditLedger.sequence_id.desc())
        .limit(1)
        .with_for_update()          # pessimistic lock prevents race conditions on seq
    )
    result = await db.execute(stmt)
    last_hash: Optional[str] = result.scalar_one_or_none()

    if last_hash is None:
        # Genesis block – chain starts from the well-known constant
        prev_hash = settings.GENESIS_HASH
    else:
        prev_hash = last_hash

    # --- Step 2: Compute hash -------------------------------------------
    current_hash = _compute_hash(
        prev_hash=prev_hash,
        entity_id=entity_id,
        field_changes=field_changes,
        modified_by=modified_by,
        timestamp=now,
    )

    # --- Step 3: Insert --------------------------------------------------
    entry = AlcoaAuditLedger(
        entity_name=entity_name,
        entity_id=entity_id,
        action_type=action_type,
        field_changes=field_changes,
        modified_by=modified_by,
        timestamp=now,
        prev_hash=prev_hash,
        current_hash=current_hash,
    )
    db.add(entry)
    await db.flush()   # get sequence_id without committing
    return entry


# ---------------------------------------------------------------------------
# Public service: verify chain integrity
# ---------------------------------------------------------------------------
class ChainVerificationResult:
    def __init__(
        self,
        status: str,       # "VERIFIED_SECURE" | "TAMPER_DETECTED"
        total_blocks: int,
        tampered_sequence_ids: list[int],
    ) -> None:
        self.status = status
        self.total_blocks = total_blocks
        self.tampered_sequence_ids = tampered_sequence_ids

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "total_blocks": self.total_blocks,
            "tampered_sequence_ids": self.tampered_sequence_ids,
        }


async def verify_audit_chain(db: AsyncSession) -> ChainVerificationResult:
    """
    Traverse the entire alcoa_audit_ledger from sequence_id=1 to latest,
    recompute each block's hash, and compare with stored hash.

    Returns TAMPER_DETECTED with exact sequence IDs if any mismatch is found.
    """
    stmt = select(AlcoaAuditLedger).order_by(AlcoaAuditLedger.sequence_id.asc())
    result = await db.execute(stmt)
    rows: list[AlcoaAuditLedger] = list(result.scalars().all())

    tampered: list[int] = []
    expected_prev = settings.GENESIS_HASH

    for row in rows:
        # Validate prev_hash linkage
        if row.prev_hash != expected_prev:
            tampered.append(row.sequence_id)

        # Recompute hash
        recomputed = _compute_hash(
            prev_hash=row.prev_hash,
            entity_id=row.entity_id,
            field_changes=row.field_changes,
            modified_by=row.modified_by,
            timestamp=row.timestamp,
        )

        if recomputed != row.current_hash:
            if row.sequence_id not in tampered:
                tampered.append(row.sequence_id)

        # Advance expected prev for next block
        expected_prev = row.current_hash

    status = "VERIFIED_SECURE" if not tampered else "TAMPER_DETECTED"
    return ChainVerificationResult(
        status=status,
        total_blocks=len(rows),
        tampered_sequence_ids=sorted(tampered),
    )
