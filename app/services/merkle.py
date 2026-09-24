import hashlib
import os
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AlcoaAuditLedger

WITNESS_STORE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "witness_merkle_store.txt"
)


def build_merkle_tree(leaf_hashes: List[str]) -> str:
    if not leaf_hashes:
        return hashlib.sha256(b"").hexdigest()
    if len(leaf_hashes) == 1:
        return leaf_hashes[0]

    current_level = list(leaf_hashes)
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            combined = hashlib.sha256((left + right).encode("utf-8")).hexdigest()
            next_level.append(combined)
        current_level = next_level

    return current_level[0]


def get_notarized_root() -> Optional[str]:
    if not os.path.exists(WITNESS_STORE_PATH):
        return None
    try:
        with open(WITNESS_STORE_PATH, "r", encoding="utf-8") as f:
            val = f.read().strip()
            return val if val else None
    except Exception:
        return None


def set_notarized_root(root: Optional[str]) -> None:
    os.makedirs(os.path.dirname(WITNESS_STORE_PATH), exist_ok=True)
    if root is None:
        if os.path.exists(WITNESS_STORE_PATH):
            os.remove(WITNESS_STORE_PATH)
    else:
        with open(WITNESS_STORE_PATH, "w", encoding="utf-8") as f:
            f.write(root.strip())


async def notarize_current_ledger(db: AsyncSession) -> str:
    stmt = select(AlcoaAuditLedger.current_hash).order_by(AlcoaAuditLedger.sequence_id.asc())
    result = await db.execute(stmt)
    hashes = list(result.scalars().all())
    root = build_merkle_tree(hashes)
    set_notarized_root(root)
    return root
