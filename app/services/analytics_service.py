import time
from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    AdverseEvent,
    AEStatus,
    ClinicalTrial,
    ConsentStatus,
    TrialPatient,
    TrialStatus,
)

_CACHE_TTL_SECONDS = 60
_kpi_cache: Optional[dict[str, Any]] = None
_cache_timestamp: float = 0.0


def invalidate_kpi_cache() -> None:
    global _kpi_cache, _cache_timestamp
    _kpi_cache = None
    _cache_timestamp = 0.0


async def compute_portfolio_kpis(db: AsyncSession) -> dict[str, Any]:
    trials_res = await db.execute(select(ClinicalTrial))
    trials = trials_res.scalars().all()
    total_trials = len(trials)

    status_counts: dict[str, int] = {
        TrialStatus.DRAFT.value: 0,
        TrialStatus.IEC_APPROVED.value: 0,
        TrialStatus.CTRI_LINKED.value: 0,
        TrialStatus.RECRUITING.value: 0,
        TrialStatus.CLOSED.value: 0,
    }
    for t in trials:
        s_val = t.status.value if hasattr(t.status, "value") else str(t.status)
        status_counts[s_val] = status_counts.get(s_val, 0) + 1

    trial_portfolio: dict[str, Any] = {
        "total_trials": total_trials,
        "by_status": dict(status_counts),
        **status_counts,
    }

    patients_res = await db.execute(select(TrialPatient))
    patients = patients_res.scalars().all()
    total_enrolled = len(patients)

    active_count = sum(1 for p in patients if p.consent_status == ConsentStatus.OBTAINED)
    withdrawn_count = sum(1 for p in patients if p.consent_status == ConsentStatus.WITHDRAWN)

    prakriti_distribution: dict[str, int] = {}
    for p in patients:
        if p.prakriti_type:
            prakriti_distribution[p.prakriti_type] = (
                prakriti_distribution.get(p.prakriti_type, 0) + 1
            )

    patient_metrics: dict[str, Any] = {
        "total_enrolled": total_enrolled,
        "active": active_count,
        "withdrawn": withdrawn_count,
        "prakriti_distribution": prakriti_distribution,
    }

    ae_res = await db.execute(select(AdverseEvent))
    all_aes = ae_res.scalars().all()
    total_adverse_events = len(all_aes)
    total_saes = sum(1 for ae in all_aes if ae.is_serious)

    now = datetime.now(tz=timezone.utc)
    active_24h_clocks = sum(
        1
        for ae in all_aes
        if ae.is_serious
        and ae.status in (AEStatus.OPEN, AEStatus.UNDER_REVIEW)
        and ae.sla_deadline is not None
        and ae.sla_deadline > now
    )
    flagged_herb_drug = sum(1 for ae in all_aes if ae.has_conflict)

    safety_kpis: dict[str, Any] = {
        "total_adverse_events": total_adverse_events,
        "total_saes": total_saes,
        "active_24h_clocks": active_24h_clocks,
        "flagged_herb_drug_interactions": flagged_herb_drug,
    }

    if total_saes == 0:
        compliance_rate = 100.0
    else:
        breached_saes = sum(
            1
            for ae in all_aes
            if ae.is_serious
            and ae.sla_deadline is not None
            and ae.sla_deadline <= now
            and ae.status in (AEStatus.OPEN, AEStatus.UNDER_REVIEW)
        )
        compliant_saes = total_saes - breached_saes
        compliance_rate = round((compliant_saes / total_saes) * 100.0, 2)

    return {
        "trial_portfolio": trial_portfolio,
        "patient_metrics": patient_metrics,
        "safety_kpis": safety_kpis,
        "compliance_rate": compliance_rate,
        "cached": False,
        "generated_at": now,
    }


async def get_portfolio_kpis(
    db: AsyncSession,
    force_refresh: bool = False,
) -> dict[str, Any]:
    global _kpi_cache, _cache_timestamp
    current_time = time.time()

    if not force_refresh and _kpi_cache is not None and (current_time - _cache_timestamp) < _CACHE_TTL_SECONDS:
        cached_result = dict(_kpi_cache)
        cached_result["cached"] = True
        return cached_result

    fresh_result = await compute_portfolio_kpis(db)
    _kpi_cache = dict(fresh_result)
    _cache_timestamp = current_time
    return fresh_result
