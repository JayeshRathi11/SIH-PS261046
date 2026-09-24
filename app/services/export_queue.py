import uuid
import traceback
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.clinical import DeadLetterExport


async def process_export_with_dead_letter_isolation(
    trial_id: uuid.UUID,
    records: List[Dict[str, Any]],
    export_type: str,
    db: AsyncSession,
) -> Dict[str, Any]:
    valid_records: List[Dict[str, Any]] = []
    quarantined_records: List[Dict[str, Any]] = []

    for record in records:
        try:
            # Check validation rules for patient export record
            record_id = record.get("usubjid") or record.get("record_identifier") or record.get("id")
            if not record_id or record.get("_is_corrupt") is True or record.get("invalid_syntax") is True:
                raise ValueError(
                    f"Malformed record payload: missing valid subject identifier or explicitly corrupt. Identifier='{record_id}'"
                )

            # Check if domain-specific critical fields are present
            if export_type == "CDISC_SDTM":
                if "domain" in record and not record["domain"]:
                    raise ValueError("CDISC record missing required DOMAIN identifier.")

            valid_records.append(record)

        except Exception as exc:
            err_trace = f"{type(exc).__name__}: {str(exc)}\n{traceback.format_exc()}"
            identifier = str(record.get("usubjid") or record.get("record_identifier") or "UNKNOWN_RECORD")
            
            dead_letter = DeadLetterExport(
                trial_id=trial_id,
                export_type=export_type,
                record_identifier=identifier,
                payload_snapshot=record,
                error_trace=err_trace,
                retry_count=0,
                status="ISOLATED",
            )
            db.add(dead_letter)
            await db.flush()
            quarantined_records.append({
                "id": str(dead_letter.id),
                "record_identifier": identifier,
                "error": str(exc),
                "status": "ISOLATED",
            })

    await db.commit()

    return {
        "trial_id": str(trial_id),
        "export_type": export_type,
        "total_records": len(records),
        "successful_count": len(valid_records),
        "quarantined_count": len(quarantined_records),
        "status": "COMPLETED_WITH_ISOLATIONS" if quarantined_records else "COMPLETED_CLEAN",
        "valid_records": valid_records,
        "quarantined_records": quarantined_records,
    }


async def get_quarantined_records_for_trial(
    trial_id: uuid.UUID,
    db: AsyncSession,
) -> List[DeadLetterExport]:
    stmt = (
        select(DeadLetterExport)
        .where(DeadLetterExport.trial_id == trial_id)
        .order_by(DeadLetterExport.quarantined_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
