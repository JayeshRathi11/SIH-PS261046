"""
AyuTrial-CTMS – Audit Router
GET /api/v1/audit/verify-chain
"""
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.schemas.clinical import ChainVerificationOut
from app.services.audit import verify_audit_chain
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/audit", tags=["ALCOA+ Audit Chain"])


@router.get(
    "/verify-chain",
    response_model=ChainVerificationOut,
    summary="Verify ALCOA+ SHA-256 audit chain integrity",
    description=(
        "Traverses the entire alcoa_audit_ledger from sequence 1 to latest, "
        "recomputes every SHA-256 block hash, and validates chain linkage. "
        "Returns VERIFIED_SECURE if all hashes match, or TAMPER_DETECTED with "
        "the exact tampered sequence IDs."
    ),
)
async def verify_chain(
    db: AsyncSession = Depends(get_db),
) -> ChainVerificationOut:
    result = await verify_audit_chain(db)
    return ChainVerificationOut(
        status=result.status,
        total_blocks=result.total_blocks,
        tampered_sequence_ids=result.tampered_sequence_ids,
    )
