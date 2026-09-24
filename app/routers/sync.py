import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import AuditAction, ECRFRecord, TrialPatient
from app.services.audit import append_audit_entry

router = APIRouter(prefix="/api/v1/sync", tags=["Offline-First Conflict-Aware Sync Batch Engine"])


class OfflineECRFMutation(BaseModel):
    client_mutation_id: str = Field(..., description="Client-generated unique mutation identifier")
    patient_id: uuid.UUID = Field(..., description="Target patient UUID")
    visit_number: int = Field(..., ge=1, description="Sequential protocol visit number")
    visit_name: str = Field(..., description="Descriptive visit name")
    form_data: Dict[str, Any] = Field(..., description="Form fields recorded offline")
    client_timestamp: datetime = Field(..., description="ISO 8601 client timestamp when offline record was created/modified")


class OfflineBatchSyncRequest(BaseModel):
    trial_id: uuid.UUID
    site_id: Optional[uuid.UUID] = None
    mutations: List[OfflineECRFMutation]


def to_utc_aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@router.post(
    "/offline-batch",
    status_code=status.HTTP_200_OK,
    summary="Batch resolve queued offline eCRF mutations with conflict-aware timestamps",
)
async def sync_offline_batch(
    payload: OfflineBatchSyncRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    inserted_count = 0
    client_win_count = 0
    server_win_count = 0

    for mut in payload.mutations:
        client_ts = to_utc_aware(mut.client_timestamp)

        # Check if record for patient_id + visit_number exists
        stmt = select(ECRFRecord).where(
            ECRFRecord.patient_id == mut.patient_id,
            ECRFRecord.visit_number == mut.visit_number,
        )
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing is None:
            # Clean Insert
            record = ECRFRecord(
                patient_id=mut.patient_id,
                trial_id=payload.trial_id,
                site_id=payload.site_id,
                visit_number=mut.visit_number,
                visit_name=mut.visit_name,
                form_data=mut.form_data,
                recorded_at=client_ts,
                updated_at=client_ts,
            )
            db.add(record)
            await db.flush()

            # Append to ALCOA+ Audit Ledger
            await append_audit_entry(
                db,
                entity_name="ecrf_records",
                entity_id=str(record.id),
                action_type=AuditAction.INSERT,
                field_changes={
                    "patient_id": str(mut.patient_id),
                    "visit_number": mut.visit_number,
                    "form_data": mut.form_data,
                    "sync_mode": "OFFLINE_CLEAN_INSERT",
                },
                modified_by="offline_sync_client",
            )

            inserted_count += 1
            results.append({
                "client_mutation_id": mut.client_mutation_id,
                "ecrf_id": str(record.id),
                "patient_id": str(mut.patient_id),
                "visit_number": mut.visit_number,
                "status": "INSERTED_CLEAN",
                "message": "Record inserted cleanly into server database.",
            })

        else:
            # Conflict Resolution: compare timestamps
            server_ts = to_utc_aware(existing.updated_at or existing.recorded_at)

            if client_ts > server_ts:
                # Client Win: Client has newer data
                existing.form_data = mut.form_data
                existing.visit_name = mut.visit_name
                existing.updated_at = client_ts
                await db.flush()

                await append_audit_entry(
                    db,
                    entity_name="ecrf_records",
                    entity_id=str(existing.id),
                    action_type=AuditAction.UPDATE,
                    field_changes={
                        "form_data": mut.form_data,
                        "conflict_resolution": "RESOLVED_CLIENT_WIN",
                        "client_timestamp": client_ts.isoformat(),
                        "server_previous_timestamp": server_ts.isoformat(),
                    },
                    modified_by="offline_sync_client",
                )

                client_win_count += 1
                results.append({
                    "client_mutation_id": mut.client_mutation_id,
                    "ecrf_id": str(existing.id),
                    "patient_id": str(mut.patient_id),
                    "visit_number": mut.visit_number,
                    "status": "RESOLVED_CLIENT_WIN",
                    "message": "Client timestamp was newer; record updated with conflict resolution logged.",
                })
            else:
                # Server Win: Server has newer or equal version
                server_win_count += 1
                results.append({
                    "client_mutation_id": mut.client_mutation_id,
                    "ecrf_id": str(existing.id),
                    "patient_id": str(mut.patient_id),
                    "visit_number": mut.visit_number,
                    "status": "CONFLICT_SERVER_WIN",
                    "message": f"Client timestamp ({client_ts.isoformat()}) is older than or equal to current server record version ({server_ts.isoformat()}). Overwrite rejected to prevent data loss.",
                })

    await db.commit()

    return {
        "trial_id": str(payload.trial_id),
        "total_mutations": len(payload.mutations),
        "inserted_count": inserted_count,
        "client_win_count": client_win_count,
        "server_win_count": server_win_count,
        "results": results,
    }
