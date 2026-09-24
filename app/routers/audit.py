import uuid
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import AccessAuditLog, AlcoaAuditLedger
from app.schemas.clinical import AccessAuditLogOut, ChainVerificationOut
from app.services.audit import verify_audit_chain
from app.services.merkle import (
    build_merkle_tree,
    get_notarized_root,
    notarize_current_ledger,
)

router = APIRouter(prefix="/api/v1/audit", tags=["ALCOA+ Audit Chain & Merkle Witness"])


@router.get(
    "/verify-chain",
    response_model=ChainVerificationOut,
    summary="Verify ALCOA+ SHA-256 audit chain integrity and Merkle witness root",
)
async def verify_chain(
    db: AsyncSession = Depends(get_db),
) -> ChainVerificationOut:
    linear_result = await verify_audit_chain(db)

    stmt = select(AlcoaAuditLedger.current_hash).order_by(AlcoaAuditLedger.sequence_id.asc())
    hashes_res = await db.execute(stmt)
    hashes = list(hashes_res.scalars().all())

    local_merkle_root = build_merkle_tree(hashes) if hashes else None
    witness_root = get_notarized_root()

    if linear_result.status == "TAMPER_DETECTED":
        return ChainVerificationOut(
            status="TAMPER_DETECTED",
            total_blocks=linear_result.total_blocks,
            tampered_sequence_ids=linear_result.tampered_sequence_ids,
            tamper_detected=True,
            reason="LINEAR_HASH_MISMATCH",
            local_merkle_root=local_merkle_root,
            witness_merkle_root=witness_root,
        )

    if witness_root is not None and local_merkle_root != witness_root:
        return ChainVerificationOut(
            status="TAMPER_DETECTED",
            total_blocks=linear_result.total_blocks,
            tampered_sequence_ids=[],
            tamper_detected=True,
            reason="WITNESS_ROOT_MISMATCH",
            local_merkle_root=local_merkle_root,
            witness_merkle_root=witness_root,
        )

    return ChainVerificationOut(
        status="VERIFIED_SECURE",
        total_blocks=linear_result.total_blocks,
        tampered_sequence_ids=[],
        tamper_detected=False,
        local_merkle_root=local_merkle_root,
        witness_merkle_root=witness_root,
    )


@router.post(
    "/notarize-witness",
    summary="Notarize current ledger into isolated witness Merkle anchor",
)
async def notarize_witness(
    db: AsyncSession = Depends(get_db),
) -> dict:
    root = await notarize_current_ledger(db)
    return {
        "status": "NOTARIZED",
        "merkle_root": root,
    }


@router.get(
    "/access-logs/{patient_id}",
    response_model=List[AccessAuditLogOut],
    summary="Get longitudinal inspection history for data protection audits",
)
async def get_patient_access_logs(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> List[AccessAuditLogOut]:
    stmt = (
        select(AccessAuditLog)
        .where(AccessAuditLog.patient_id == patient_id)
        .order_by(AccessAuditLog.accessed_at.asc())
    )
    res = await db.execute(stmt)
    logs = res.scalars().all()
    return [AccessAuditLogOut.model_validate(log) for log in logs]
