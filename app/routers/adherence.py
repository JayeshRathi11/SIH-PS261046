import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clinical import AuditAction, PatientAdherenceLog, TrialPatient
from app.services.audit import append_audit_entry

router = APIRouter(prefix="/api/v1/adherence", tags=["Patient Medication Adherence & Webhooks"])


class TelegramLinkRequest(BaseModel):
    patient_id: uuid.UUID
    telegram_chat_id: str


def parse_dosage_status(text: str) -> str:
    cleaned = text.strip().lower()
    if any(k in cleaned for k in ["taken", "maine dawa li", "dawa li", "yes", "ha", "haan", "le li"]):
        return "TAKEN"
    if any(k in cleaned for k in ["missed", "miss ho gayi", "miss", "no", "nahi", "chhoot gayi"]):
        return "MISSED"
    return "TAKEN" if "take" in cleaned else "MISSED"


@router.post(
    "/link-telegram",
    summary="Link a patient to a Telegram Chat ID",
)
async def link_telegram_chat(
    payload: TelegramLinkRequest,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    stmt = select(TrialPatient).where(TrialPatient.id == payload.patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )
    patient.telegram_chat_id = str(payload.telegram_chat_id)
    await db.commit()
    await db.refresh(patient)
    return {
        "status": "LINKED",
        "patient_id": str(patient.id),
        "usubjid": patient.usubjid,
        "telegram_chat_id": patient.telegram_chat_id,
    }


@router.post(
    "/telegram-webhook",
    status_code=status.HTTP_200_OK,
    summary="Telegram Bot Webhook for patient dose compliance updates",
)
async def telegram_adherence_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    body: Dict[str, Any] = await request.json()

    chat_id: Optional[str] = None
    raw_status: Optional[str] = None

    # Handle standard Telegram CallbackQuery (Inline buttons "Maine Dawa Li" / "Miss Ho Gayi")
    if "callback_query" in body:
        cb = body["callback_query"]
        chat_id = str(cb.get("from", {}).get("id") or cb.get("message", {}).get("chat", {}).get("id") or "")
        raw_status = str(cb.get("data", ""))

    # Handle standard Telegram message
    elif "message" in body:
        msg = body["message"]
        chat_id = str(msg.get("chat", {}).get("id") or msg.get("from", {}).get("id") or "")
        raw_status = str(msg.get("text", ""))

    # Handle direct/mock JSON payload
    elif "telegram_chat_id" in body:
        chat_id = str(body["telegram_chat_id"])
        raw_status = str(body.get("dosage_status") or body.get("status") or "")

    # Direct patient_id fallback for internal testing
    patient_id_direct = body.get("patient_id")

    if not chat_id and not patient_id_direct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to extract telegram_chat_id or patient_id from payload.",
        )

    # Resolve patient
    patient: Optional[TrialPatient] = None
    if chat_id:
        from sqlalchemy import or_
        stmt = select(TrialPatient).where(
            or_(
                TrialPatient.telegram_chat_id == chat_id,
                TrialPatient.telegram_chat_id == f"tg_{chat_id}",
                TrialPatient.telegram_chat_id == f"tg_user_{chat_id}",
            )
        )
        res = await db.execute(stmt)
        patient = res.scalar_one_or_none()

    if not patient and patient_id_direct:
        try:
            pid = uuid.UUID(str(patient_id_direct))
            stmt = select(TrialPatient).where(TrialPatient.id == pid)
            res = await db.execute(stmt)
            patient = res.scalar_one_or_none()
        except ValueError:
            pass

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No patient found registered with telegram_chat_id '{chat_id}'.",
        )

    dosage_status = parse_dosage_status(raw_status or "TAKEN")

    adherence_log = PatientAdherenceLog(
        patient_id=patient.id,
        telegram_chat_id=chat_id,
        dosage_status=dosage_status,
        reported_via="TELEGRAM_BOT",
    )
    db.add(adherence_log)
    await db.flush()

    # Append to ALCOA+ Audit Ledger
    await append_audit_entry(
        db,
        entity_name="patient_adherence_logs",
        entity_id=str(adherence_log.id),
        action_type=AuditAction.INSERT,
        field_changes={
            "patient_id": str(patient.id),
            "usubjid": patient.usubjid,
            "dosage_status": dosage_status,
            "telegram_chat_id": chat_id,
            "reported_via": "TELEGRAM_BOT",
        },
        modified_by="telegram_bot",
    )

    await db.commit()
    await db.refresh(adherence_log)

    return {
        "status": "RECORDED",
        "log_id": str(adherence_log.id),
        "patient_id": str(patient.id),
        "usubjid": patient.usubjid,
        "dosage_status": dosage_status,
        "recorded_at": adherence_log.recorded_at.isoformat(),
    }


@router.get(
    "/{patient_id}",
    summary="Get patient adherence compliance metrics and history",
)
async def get_patient_adherence(
    patient_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    stmt_p = select(TrialPatient).where(TrialPatient.id == patient_id)
    res_p = await db.execute(stmt_p)
    patient = res_p.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    stmt_logs = (
        select(PatientAdherenceLog)
        .where(PatientAdherenceLog.patient_id == patient_id)
        .order_by(PatientAdherenceLog.recorded_at.desc())
    )
    res_logs = await db.execute(stmt_logs)
    logs = res_logs.scalars().all()

    total_reported = len(logs)
    dosages_taken = sum(1 for log in logs if log.dosage_status == "TAKEN")
    dosages_missed = sum(1 for log in logs if log.dosage_status == "MISSED")

    compliance_percentage = (
        round((dosages_taken / total_reported) * 100.0, 2)
        if total_reported > 0
        else 100.0
    )

    return {
        "patient_id": str(patient.id),
        "usubjid": patient.usubjid,
        "total_reported": total_reported,
        "dosages_taken": dosages_taken,
        "dosages_missed": dosages_missed,
        "compliance_percentage": compliance_percentage,
        "history": [
            {
                "id": str(l.id),
                "dosage_status": l.dosage_status,
                "reported_via": l.reported_via,
                "recorded_at": l.recorded_at.isoformat() if l.recorded_at else None,
            }
            for l in logs
        ],
    }
