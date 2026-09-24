import asyncio
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import AsyncSessionLocal
from app.models.clinical import AdverseEvent, AEStatus
from app.services.watchdog import record_daemon_heartbeat

router = APIRouter(tags=["Real-Time WebSockets"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()


def compute_countdown_payload(ae: AdverseEvent) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    if ae.sla_deadline:
        remaining_seconds = max(0, int((ae.sla_deadline - now).total_seconds()))
    else:
        remaining_seconds = 86400

    if remaining_seconds <= 0:
        sla_status = "SLA_BREACHED"
        threshold_alert = "BREACHED"
    elif remaining_seconds <= 4 * 3600:
        sla_status = "CRITICAL_WINDOW_ACTIVE"
        threshold_alert = "T-4h"
    elif remaining_seconds <= 12 * 3600:
        sla_status = "CRITICAL_WINDOW_ACTIVE"
        threshold_alert = "T-12h"
    else:
        sla_status = "CRITICAL_WINDOW_ACTIVE"
        threshold_alert = "T-24h"

    usubjid = "UNKNOWN"
    if ae.patient and getattr(ae.patient, "usubjid", None):
        usubjid = ae.patient.usubjid

    return {
        "ae_id": str(ae.id),
        "patient_usubjid": usubjid,
        "remaining_seconds": remaining_seconds,
        "sla_status": sla_status,
        "threshold_alert": threshold_alert,
    }


async def broadcast_sae_alert(ae: AdverseEvent):
    payload = compute_countdown_payload(ae)
    payload["event"] = "NEW_SAE_ESCALATION"
    await manager.broadcast(payload)


@router.websocket("/ws/sla-countdown")
async def websocket_sla_countdown(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                select(AdverseEvent)
                .options(joinedload(AdverseEvent.patient))
                .where(
                    AdverseEvent.is_serious == True,
                    AdverseEvent.status.in_([AEStatus.OPEN, AEStatus.UNDER_REVIEW]),
                )
            )
            res = await session.execute(stmt)
            open_saes = res.scalars().all()

        record_daemon_heartbeat()
        if open_saes:
            for sae in open_saes:
                await websocket.send_json(compute_countdown_payload(sae))
        else:
            await websocket.send_json({
                "type": "HEARTBEAT",
                "active_sae_count": 0,
                "message": "NO_ACTIVE_SAE_COUNTDOWN",
            })

        while True:
            await asyncio.sleep(1)
            record_daemon_heartbeat()
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(AdverseEvent)
                    .options(joinedload(AdverseEvent.patient))
                    .where(
                        AdverseEvent.is_serious == True,
                        AdverseEvent.status.in_([AEStatus.OPEN, AEStatus.UNDER_REVIEW]),
                    )
                )
                res = await session.execute(stmt)
                current_saes = res.scalars().all()

            for sae in current_saes:
                await websocket.send_json(compute_countdown_payload(sae))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
    finally:
        manager.disconnect(websocket)
