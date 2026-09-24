import threading
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AdverseEvent, AEStatus

_lock = threading.Lock()
_last_daemon_heartbeat: Optional[datetime] = None


def record_daemon_heartbeat(timestamp: Optional[datetime] = None) -> None:
    global _last_daemon_heartbeat
    with _lock:
        _last_daemon_heartbeat = timestamp or datetime.now(tz=timezone.utc)


def set_daemon_heartbeat_time(timestamp: Optional[datetime]) -> None:
    global _last_daemon_heartbeat
    with _lock:
        _last_daemon_heartbeat = timestamp


def get_last_daemon_heartbeat() -> Optional[datetime]:
    with _lock:
        return _last_daemon_heartbeat


def get_watchdog_status(max_staleness_seconds: int = 30) -> dict[str, Any]:
    now = datetime.now(tz=timezone.utc)
    last_hb = get_last_daemon_heartbeat()

    if last_hb is None:
        return {
            "status": "DEGRADED_STALE_DAEMON",
            "is_healthy": False,
            "last_heartbeat": None,
            "staleness_seconds": None,
            "max_staleness_seconds": max_staleness_seconds,
            "checked_at": now.isoformat(),
            "message": "Daemon heartbeat not recorded yet.",
        }

    staleness = (now - last_hb).total_seconds()
    if staleness <= max_staleness_seconds:
        return {
            "status": "HEALTHY",
            "is_healthy": True,
            "last_heartbeat": last_hb.isoformat(),
            "staleness_seconds": round(staleness, 2),
            "max_staleness_seconds": max_staleness_seconds,
            "checked_at": now.isoformat(),
        }
    else:
        return {
            "status": "DEGRADED_STALE_DAEMON",
            "is_healthy": False,
            "last_heartbeat": last_hb.isoformat(),
            "staleness_seconds": round(staleness, 2),
            "max_staleness_seconds": max_staleness_seconds,
            "checked_at": now.isoformat(),
            "message": f"Daemon heartbeat stale by {round(staleness, 2)}s (max allowed: {max_staleness_seconds}s).",
        }


async def get_unacknowledged_saes_diagnostics(db: AsyncSession) -> list[dict[str, Any]]:
    stmt = (
        select(AdverseEvent)
        .where(
            AdverseEvent.is_serious == True,
            AdverseEvent.status.in_([AEStatus.OPEN, AEStatus.UNDER_REVIEW]),
        )
        .order_by(AdverseEvent.sla_deadline.asc())
    )
    res = await db.execute(stmt)
    saes = res.scalars().all()
    now = datetime.now(tz=timezone.utc)
    return [
        {
            "ae_id": str(sae.id),
            "patient_id": str(sae.patient_id),
            "severity": sae.severity.value,
            "sla_deadline": sae.sla_deadline.isoformat() if sae.sla_deadline else None,
            "is_overdue": sae.sla_deadline <= now if sae.sla_deadline else False,
        }
        for sae in saes
    ]
