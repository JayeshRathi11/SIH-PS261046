import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.clinical import (
    AlcoaAuditLedger,
    AuditAction,
    ClinicalTrial,
    ConsentStatus,
    ECRFRecord,
    TrialPatient,
    TrialSite,
    TrialStatus,
)
from app.services.audit import append_audit_entry


async def seed_demo_data(db: AsyncSession) -> dict[str, Any]:
    stmt_s1 = select(TrialSite).where(TrialSite.site_code == "SITE-01")
    res_s1 = await db.execute(stmt_s1)
    site1 = res_s1.scalar_one_or_none()
    if site1 is None:
        site1 = TrialSite(
            site_code="SITE-01",
            site_name="AIIA New Delhi Apex Centre",
            city="New Delhi",
            is_active=True,
        )
        db.add(site1)

    stmt_s2 = select(TrialSite).where(TrialSite.site_code == "SITE-02")
    res_s2 = await db.execute(stmt_s2)
    site2 = res_s2.scalar_one_or_none()
    if site2 is None:
        site2 = TrialSite(
            site_code="SITE-02",
            site_name="Peripheral Research Centre",
            city="Jamnagar",
            is_active=True,
        )
        db.add(site2)

    await db.flush()

    stmt_trial = select(ClinicalTrial).where(ClinicalTrial.protocol_id == "AIIA-GUD-2026")
    res_trial = await db.execute(stmt_trial)
    trial = res_trial.scalar_one_or_none()
    if trial is None:
        trial = ClinicalTrial(
            protocol_id="AIIA-GUD-2026",
            ctri_registration_id="CTRI/2026/04/091234",
            iec_clearance_number="IEC/AIIA/2026/108",
            study_title="Phase-2 Evaluation of Standardized Guduchi Formulation in Metabolic Syndrome",
            status=TrialStatus.RECRUITING,
        )
        db.add(trial)
        await db.flush()
        await append_audit_entry(
            db,
            entity_name="clinical_trials",
            entity_id=str(trial.id),
            action_type=AuditAction.INSERT,
            field_changes={
                "protocol_id": trial.protocol_id,
                "status": trial.status.value,
                "study_title": trial.study_title,
            },
            modified_by="system_seeder",
        )

    demo_usubjid = "AIIA-P089"
    stmt_demo = select(TrialPatient).where(
        TrialPatient.trial_id == trial.id,
        TrialPatient.usubjid == demo_usubjid,
    )
    res_demo = await db.execute(stmt_demo)
    demo_patient = res_demo.scalar_one_or_none()
    if demo_patient is None:
        demo_patient = TrialPatient(
            trial_id=trial.id,
            site_id=site1.id,
            usubjid=demo_usubjid,
            prakriti_type="PITTA_KAPHA",
            baseline_agni="TIKSHNA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db.add(demo_patient)
        await db.flush()
        await append_audit_entry(
            db,
            entity_name="trial_patients",
            entity_id=str(demo_patient.id),
            action_type=AuditAction.INSERT,
            field_changes={
                "usubjid": demo_patient.usubjid,
                "trial_id": str(trial.id),
                "site_id": str(site1.id),
                "prakriti_type": "PITTA_KAPHA",
                "active_arm": "Guduchi Extract 500mg BD",
                "concomitant_drugs": ["Aspirin 75mg OD"],
            },
            modified_by="system_seeder",
        )

        v1_data = {
            "vital_signs": {"systolic_bp": 134, "diastolic_bp": 88, "heart_rate": 76},
            "liver_enzymes": {"alt_u_l": 32, "ast_u_l": 28, "bilirubin_mg_dl": 0.8},
            "active_intervention": "Guduchi Extract 500mg BD",
            "concomitant_medications": ["Aspirin 75mg OD"],
            "dosage_compliance_pct": 100.0,
            "interval_days": 0.0,
        }
        ecrf_v1 = ECRFRecord(
            patient_id=demo_patient.id,
            trial_id=trial.id,
            site_id=site1.id,
            visit_number=1,
            visit_name="Day 0 - Baseline",
            form_data=v1_data,
        )
        db.add(ecrf_v1)
        await db.flush()
        await append_audit_entry(
            db,
            entity_name="ecrf_records",
            entity_id=str(ecrf_v1.id),
            action_type=AuditAction.INSERT,
            field_changes=v1_data,
            modified_by="system_seeder",
        )

        v2_data = {
            "vital_signs": {"systolic_bp": 130, "diastolic_bp": 84, "heart_rate": 78},
            "liver_enzymes": {"alt_u_l": 165, "ast_u_l": 142, "bilirubin_mg_dl": 2.4},
            "active_intervention": "Guduchi Extract 500mg BD",
            "concomitant_medications": ["Aspirin 75mg OD"],
            "clinical_notes": "Jaundice and nausea reported with elevated transaminases",
            "dosage_compliance_pct": 100.0,
            "interval_days": 14.0,
        }
        ecrf_v2 = ECRFRecord(
            patient_id=demo_patient.id,
            trial_id=trial.id,
            site_id=site1.id,
            visit_number=2,
            visit_name="Day 14 - Treatment Follow-up",
            form_data=v2_data,
        )
        db.add(ecrf_v2)
        await db.flush()
        await append_audit_entry(
            db,
            entity_name="ecrf_records",
            entity_id=str(ecrf_v2.id),
            action_type=AuditAction.INSERT,
            field_changes=v2_data,
            modified_by="system_seeder",
        )

    prakriti_options = [
        "VATA", "PITTA", "KAPHA",
        "VATA_PITTA", "PITTA_KAPHA", "VATA_KAPHA", "TRIDOSHA"
    ]
    agni_options = ["SAMA", "VISHAMA", "TIKSHNA", "MANDA"]

    patients_created_count = 0
    for i in range(1, 21):
        subj_code = f"AIIA-P{i:03d}"
        stmt_p = select(TrialPatient).where(
            TrialPatient.trial_id == trial.id,
            TrialPatient.usubjid == subj_code,
        )
        res_p = await db.execute(stmt_p)
        existing_p = res_p.scalar_one_or_none()
        if existing_p is not None:
            continue

        assigned_site = site1 if (i % 2 == 1) else site2
        prakriti = prakriti_options[i % len(prakriti_options)]
        agni = agni_options[i % len(agni_options)]
        consent = ConsentStatus.WITHDRAWN if (i == 18) else ConsentStatus.OBTAINED

        patient = TrialPatient(
            trial_id=trial.id,
            site_id=assigned_site.id,
            usubjid=subj_code,
            prakriti_type=prakriti,
            baseline_agni=agni,
            consent_status=consent,
        )
        db.add(patient)
        await db.flush()
        patients_created_count += 1

        await append_audit_entry(
            db,
            entity_name="trial_patients",
            entity_id=str(patient.id),
            action_type=AuditAction.INSERT,
            field_changes={
                "usubjid": subj_code,
                "trial_id": str(trial.id),
                "site_id": str(assigned_site.id),
                "prakriti_type": prakriti,
                "baseline_agni": agni,
                "consent_status": consent.value,
            },
            modified_by="system_seeder",
        )

        num_visits = 3 if i <= 10 else 2
        for v in range(1, num_visits + 1):
            if i == 7 and v == 2:
                interval = 42.0
                compliance = 55.0
            else:
                interval = 14.0 + (0.5 if v == 2 else 0.0)
                compliance = 95.0 + (i % 5)

            rec_data = {
                "vital_signs": {
                    "systolic_bp": 120 + (i % 15),
                    "diastolic_bp": 78 + (i % 10),
                    "heart_rate": 72 + (i % 8),
                },
                "dosage_compliance_pct": compliance,
                "interval_days": interval if v > 1 else 0.0,
            }
            ecrf = ECRFRecord(
                patient_id=patient.id,
                trial_id=trial.id,
                site_id=assigned_site.id,
                visit_number=v,
                visit_name=f"Visit {v}",
                form_data=rec_data,
            )
            db.add(ecrf)
            await db.flush()
            await append_audit_entry(
                db,
                entity_name="ecrf_records",
                entity_id=str(ecrf.id),
                action_type=AuditAction.INSERT,
                field_changes=rec_data,
                modified_by="system_seeder",
            )

    await db.commit()

    return {
        "status": "SEEDED_SUCCESS",
        "trial_id": str(trial.id),
        "protocol_id": trial.protocol_id,
        "site_01": site1.site_code,
        "site_02": site2.site_code,
        "demo_subject": demo_usubjid,
        "total_seeded_patients": 21,
    }


async def main():
    from app.core.database import engine, Base
    from app.models import clinical  # registers models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await seed_demo_data(session)
        print("SEEDING COMPLETE:", result)


if __name__ == "__main__":
    asyncio.run(main())
