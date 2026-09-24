from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.lock_manager import lock_manager

router = APIRouter(prefix="/api/v1/locks", tags=["Real-Time Field-Level Concurrency Locking"])


class LockAcquireRequest(BaseModel):
    record_id: str = Field(..., description="Target record or eCRF ID")
    field_name: str = Field(..., description="Target field name (e.g. systolic_bp)")
    user_id: str = Field(..., description="User acquiring lock")
    ttl_seconds: int = Field(30, ge=1, le=300, description="Lock TTL in seconds (default 30)")


class LockReleaseRequest(BaseModel):
    record_id: str = Field(..., description="Target record or eCRF ID")
    field_name: str = Field(..., description="Target field name (e.g. systolic_bp)")
    user_id: str = Field(..., description="User releasing lock")


@router.post(
    "/acquire",
    summary="Acquire a field-level concurrency lock",
)
async def acquire_lock(payload: LockAcquireRequest) -> Dict[str, Any]:
    acquired, lock_holder = lock_manager.acquire_field_lock(
        record_id=payload.record_id,
        field_name=payload.field_name,
        user_id=payload.user_id,
        ttl_seconds=payload.ttl_seconds,
    )
    if not acquired:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "Field is currently locked by another user",
                "lock_holder": lock_holder,
                "record_id": payload.record_id,
                "field_name": payload.field_name,
            },
        )
    return {
        "status": "ACQUIRED",
        "record_id": payload.record_id,
        "field_name": payload.field_name,
        "user_id": payload.user_id,
        "ttl_seconds": payload.ttl_seconds,
    }


@router.post(
    "/release",
    summary="Release a field-level concurrency lock",
)
async def release_lock(payload: LockReleaseRequest) -> Dict[str, Any]:
    released = lock_manager.release_field_lock(
        record_id=payload.record_id,
        field_name=payload.field_name,
        user_id=payload.user_id,
    )
    if not released:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot release lock held by another user",
        )
    return {
        "status": "RELEASED",
        "record_id": payload.record_id,
        "field_name": payload.field_name,
        "user_id": payload.user_id,
    }


@router.get(
    "/{record_id}",
    summary="Get all active field locks on a record",
)
async def get_locks(record_id: str) -> Dict[str, Any]:
    active = lock_manager.get_active_locks(record_id)
    return {
        "record_id": record_id,
        "active_locks": active,
    }
