import math
import statistics
import uuid
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import ECRFRecord, TrialPatient


def compute_z_score(value: float, mean: float, std_dev: float) -> float:
    if std_dev <= 0.000001:
        return 0.0
    return abs(value - mean) / std_dev


def is_spc_anomaly(z_score: float, threshold: float = 2.5) -> bool:
    return z_score > threshold


def calculate_mean_and_stdev(values: list[float]) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], 0.0
    m = statistics.mean(values)
    s = statistics.stdev(values)
    return m, s


async def analyze_trial_protocol_deviations(
    db: AsyncSession,
    trial_id: uuid.UUID,
) -> dict[str, Any]:
    stmt = (
        select(ECRFRecord)
        .options(joinedload(ECRFRecord.patient))
        .where(ECRFRecord.trial_id == trial_id)
        .order_by(ECRFRecord.patient_id.asc(), ECRFRecord.visit_number.asc())
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    patient_records_map: dict[uuid.UUID, list[ECRFRecord]] = {}
    for r in records:
        patient_records_map.setdefault(r.patient_id, []).append(r)

    site_data_map: dict[str, dict[str, Any]] = {}

    for pid, p_recs in patient_records_map.items():
        p_recs.sort(key=lambda x: x.visit_number)
        prev_rec: Optional[ECRFRecord] = None

        for rec in p_recs:
            site_key = str(rec.site_id) if rec.site_id else (
                str(rec.patient.site_id) if rec.patient and rec.patient.site_id else "DEFAULT_SITE"
            )

            if site_key not in site_data_map:
                site_data_map[site_key] = {
                    "intervals": [],
                    "compliance": [],
                    "evaluated_records": [],
                }

            interval_val: Optional[float] = None
            if "interval_days" in rec.form_data:
                try:
                    interval_val = float(rec.form_data["interval_days"])
                except (ValueError, TypeError):
                    interval_val = None
            elif prev_rec is not None:
                delta = rec.recorded_at - prev_rec.recorded_at
                interval_val = max(0.0, delta.total_seconds() / 86400.0)

            if interval_val is not None:
                site_data_map[site_key]["intervals"].append(interval_val)

            comp_val: Optional[float] = None
            for key in ["dosage_compliance_pct", "compliance_score", "compliance", "adherence_pct"]:
                if key in rec.form_data:
                    try:
                        comp_val = float(rec.form_data[key])
                        break
                    except (ValueError, TypeError):
                        pass

            if comp_val is not None:
                site_data_map[site_key]["compliance"].append(comp_val)

            site_data_map[site_key]["evaluated_records"].append({
                "record": rec,
                "interval": interval_val,
                "compliance": comp_val,
                "usubjid": rec.patient.usubjid if rec.patient else "UNKNOWN",
            })

            prev_rec = rec

    sites_baselines: dict[str, Any] = {}
    anomalies: list[dict[str, Any]] = []
    flagged_patients_map: dict[str, dict[str, Any]] = {}

    for site_key, s_info in site_data_map.items():
        mean_int, std_int = calculate_mean_and_stdev(s_info["intervals"])
        mean_comp, std_comp = calculate_mean_and_stdev(s_info["compliance"])

        sites_baselines[site_key] = {
            "site_id": site_key,
            "total_records": len(s_info["evaluated_records"]),
            "mean_interval_days": round(mean_int, 2),
            "std_interval_days": round(std_int, 2),
            "mean_dosage_compliance": round(mean_comp, 2),
            "std_dosage_compliance": round(std_comp, 2),
        }

        for item in s_info["evaluated_records"]:
            r = item["record"]
            usubjid = item["usubjid"]
            int_val = item["interval"]
            comp_val = item["compliance"]

            if int_val is not None and std_int > 0.0:
                z_int = compute_z_score(int_val, mean_int, std_int)
                if is_spc_anomaly(z_int):
                    anomaly_entry = {
                        "ecrf_id": str(r.id),
                        "patient_id": str(r.patient_id),
                        "usubjid": usubjid,
                        "visit_number": r.visit_number,
                        "site_id": site_key,
                        "metric": "VISIT_INTERVAL",
                        "observed_value": round(int_val, 2),
                        "baseline_mean": round(mean_int, 2),
                        "baseline_std": round(std_int, 2),
                        "z_score": round(z_int, 2),
                        "anomaly_flag": "PROTOCOL_DRIFT_ANOMALY",
                    }
                    anomalies.append(anomaly_entry)
                    if usubjid not in flagged_patients_map:
                        flagged_patients_map[usubjid] = {
                            "patient_id": str(r.patient_id),
                            "usubjid": usubjid,
                            "anomaly_count": 0,
                            "risk_level": "HIGH",
                        }
                    flagged_patients_map[usubjid]["anomaly_count"] += 1

            if comp_val is not None and std_comp > 0.0:
                z_comp = compute_z_score(comp_val, mean_comp, std_comp)
                if is_spc_anomaly(z_comp):
                    anomaly_entry = {
                        "ecrf_id": str(r.id),
                        "patient_id": str(r.patient_id),
                        "usubjid": usubjid,
                        "visit_number": r.visit_number,
                        "site_id": site_key,
                        "metric": "DOSAGE_COMPLIANCE",
                        "observed_value": round(comp_val, 2),
                        "baseline_mean": round(mean_comp, 2),
                        "baseline_std": round(std_comp, 2),
                        "z_score": round(z_comp, 2),
                        "anomaly_flag": "PROTOCOL_DRIFT_ANOMALY",
                    }
                    anomalies.append(anomaly_entry)
                    if usubjid not in flagged_patients_map:
                        flagged_patients_map[usubjid] = {
                            "patient_id": str(r.patient_id),
                            "usubjid": usubjid,
                            "anomaly_count": 0,
                            "risk_level": "HIGH",
                        }
                    flagged_patients_map[usubjid]["anomaly_count"] += 1

    return {
        "trial_id": str(trial_id),
        "sites_baselines": sites_baselines,
        "anomalies": anomalies,
        "flagged_patients": list(flagged_patients_map.values()),
        "total_anomalies": len(anomalies),
    }
