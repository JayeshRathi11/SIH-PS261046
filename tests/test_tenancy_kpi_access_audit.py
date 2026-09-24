import uuid
import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import (
    ClinicalTrial,
    ConsentStatus,
    TrialPatient,
    TrialStatus,
    TrialSite,
)


@pytest.mark.asyncio
class TestMultiTenantSiteIsolation:

    async def test_clinician_can_view_own_site_patient_and_blocked_on_other_site(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        site1 = TrialSite(
            site_code="SITE-DEL-01",
            site_name="AIIA New Delhi Central",
            city="New Delhi",
            is_active=True,
        )
        site2 = TrialSite(
            site_code="SITE-JAM-02",
            site_name="AIIA Jamnagar Satellite",
            city="Jamnagar",
            is_active=True,
        )
        trial = ClinicalTrial(
            protocol_id="AIIA-TENANT-001",
            study_title="Multicenter Ashwagandha Study",
            status=TrialStatus.RECRUITING,
        )
        db_session.add_all([site1, site2, trial])
        await db_session.flush()

        p1 = TrialPatient(
            trial_id=trial.id,
            site_id=site1.id,
            usubjid="USJ-SITE1-001",
            prakriti_type="VATA_PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        p2 = TrialPatient(
            trial_id=trial.id,
            site_id=site2.id,
            usubjid="USJ-SITE2-001",
            prakriti_type="KAPHA",
            baseline_agni="MANDA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add_all([p1, p2])
        await db_session.commit()

        clinician1_headers = {
            "X-Site-Id": str(site1.id),
            "X-User-Role": "CLINICIAN",
            "X-User-Id": "dr_delhi_investigator",
        }
        res_p1 = await client.get(f"/api/v1/patients/{p1.id}", headers=clinician1_headers)
        assert res_p1.status_code == 200
        assert res_p1.json()["id"] == str(p1.id)
        assert res_p1.json()["site_id"] == str(site1.id)

        res_p2_blocked = await client.get(f"/api/v1/patients/{p2.id}", headers=clinician1_headers)
        assert res_p2_blocked.status_code == 403
        assert "Access denied" in res_p2_blocked.json()["detail"]

        clinician2_headers = {
            "X-Site-Id": str(site2.id),
            "X-User-Role": "CLINICIAN",
            "X-User-Id": "dr_jamnagar_investigator",
        }
        res_p2 = await client.get(f"/api/v1/patients/{p2.id}", headers=clinician2_headers)
        assert res_p2.status_code == 200
        assert res_p2.json()["id"] == str(p2.id)

        res_p1_blocked = await client.get(f"/api/v1/patients/{p1.id}", headers=clinician2_headers)
        assert res_p1_blocked.status_code == 403

    async def test_national_oversight_roles_bypass_site_isolation(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        site1 = TrialSite(
            site_code="SITE-MUM-01",
            site_name="AIIA Mumbai Center",
            city="Mumbai",
            is_active=True,
        )
        site2 = TrialSite(
            site_code="SITE-BLR-02",
            site_name="AIIA Bengaluru Center",
            city="Bengaluru",
            is_active=True,
        )
        trial = ClinicalTrial(
            protocol_id="AIIA-TENANT-002",
            study_title="Multicenter Triphala Study",
            status=TrialStatus.RECRUITING,
        )
        db_session.add_all([site1, site2, trial])
        await db_session.flush()

        p1 = TrialPatient(
            trial_id=trial.id,
            site_id=site1.id,
            usubjid="USJ-MUM-001",
            prakriti_type="PITTA",
            baseline_agni="TIKSHNA",
            consent_status=ConsentStatus.OBTAINED,
        )
        p2 = TrialPatient(
            trial_id=trial.id,
            site_id=site2.id,
            usubjid="USJ-BLR-001",
            prakriti_type="VATA",
            baseline_agni="VISHAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add_all([p1, p2])
        await db_session.commit()

        for role in ["NPVCC_OFFICER", "DSMB_ADMIN", "REGULATORY_AUDITOR", "SUPER_ADMIN"]:
            headers = {
                "X-User-Role": role,
                "X-User-Id": f"officer_{role.lower()}",
            }
            r1 = await client.get(f"/api/v1/patients/{p1.id}", headers=headers)
            assert r1.status_code == 200, f"Role {role} should view site1 patient"
            assert r1.json()["id"] == str(p1.id)

            r2 = await client.get(f"/api/v1/patients/{p2.id}", headers=headers)
            assert r2.status_code == 200, f"Role {role} should view site2 patient"
            assert r2.json()["id"] == str(p2.id)

    async def test_site_registration_and_listing(
        self, client: httpx.AsyncClient
    ):
        payload = {
            "site_code": f"SITE-KOL-{uuid.uuid4().hex[:4].upper()}",
            "site_name": "AIIA Kolkata Regional Center",
            "city": "Kolkata",
            "is_active": True,
        }
        res = await client.post("/api/v1/patients/sites", json=payload)
        assert res.status_code == 201
        site_data = res.json()
        assert site_data["site_code"] == payload["site_code"]
        assert site_data["city"] == "Kolkata"

        list_res = await client.get("/api/v1/patients/sites")
        assert list_res.status_code == 200
        sites = list_res.json()
        assert any(s["site_code"] == payload["site_code"] for s in sites)

    async def test_list_patients_filtered_by_site(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        site1 = TrialSite(
            site_code="SITE-PUN-01",
            site_name="AIIA Pune Center",
            city="Pune",
            is_active=True,
        )
        site2 = TrialSite(
            site_code="SITE-GOA-02",
            site_name="AIIA Goa Center",
            city="Goa",
            is_active=True,
        )
        trial = ClinicalTrial(
            protocol_id="AIIA-LIST-001",
            study_title="Multicenter Filtering Study",
            status=TrialStatus.RECRUITING,
        )
        db_session.add_all([site1, site2, trial])
        await db_session.flush()

        p1 = TrialPatient(
            trial_id=trial.id,
            site_id=site1.id,
            usubjid="USJ-PUN-001",
            prakriti_type="PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        p2 = TrialPatient(
            trial_id=trial.id,
            site_id=site2.id,
            usubjid="USJ-GOA-001",
            prakriti_type="VATA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add_all([p1, p2])
        await db_session.commit()

        clinician1_headers = {
            "X-Site-Id": str(site1.id),
            "X-User-Role": "CLINICIAN",
            "X-User-Id": "dr_pune",
        }
        res1 = await client.get("/api/v1/patients", headers=clinician1_headers)
        assert res1.status_code == 200
        patients_c1 = res1.json()
        assert len(patients_c1) == 1
        assert patients_c1[0]["id"] == str(p1.id)

        officer_headers = {
            "X-User-Role": "NPVCC_OFFICER",
            "X-User-Id": "npvcc_officer_global",
        }
        res_global = await client.get("/api/v1/patients", headers=officer_headers)
        assert res_global.status_code == 200
        patients_global = res_global.json()
        assert len(patients_global) == 2



@pytest.mark.asyncio
class TestDpdpReadAccessAuditTrail:

    async def test_patient_read_logs_purpose_and_user_in_access_audit_logs(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id="AIIA-AUDIT-001",
            study_title="Audit Trail Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-AUDIT-001",
            prakriti_type="PITTA_KAPHA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()

        headers = {
            "X-User-Role": "REGULATORY_AUDITOR",
            "X-User-Id": "cdsco_inspector_12",
        }
        res = await client.get(
            f"/api/v1/patients/{patient.id}?purpose_code=PURPOSE_REGULATORY_INSPECTION",
            headers=headers,
        )
        assert res.status_code == 200

        logs_res = await client.get(f"/api/v1/audit/access-logs/{patient.id}")
        assert logs_res.status_code == 200
        logs = logs_res.json()
        assert len(logs) == 1
        assert logs[0]["user_id"] == "cdsco_inspector_12"
        assert logs[0]["patient_id"] == str(patient.id)
        assert logs[0]["purpose_code"] == "PURPOSE_REGULATORY_INSPECTION"
        assert "accessed_at" in logs[0]

    async def test_longitudinal_access_audit_trail_order(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id="AIIA-AUDIT-002",
            study_title="Longitudinal Inspection Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-AUDIT-002",
            prakriti_type="VATA_KAPHA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()

        inspections = [
            ("dr_investigator", "CLINICIAN", "PURPOSE_CLINICAL_REVIEW"),
            ("iec_member_3", "DSMB_ADMIN", "PURPOSE_IEC_AUDIT"),
            ("cdsco_officer_7", "REGULATORY_AUDITOR", "PURPOSE_REGULATORY_INSPECTION"),
        ]

        for user_id, role, purpose in inspections:
            h = {"X-User-Id": user_id, "X-User-Role": role}
            r = await client.get(
                f"/api/v1/patients/{patient.id}?purpose_code={purpose}",
                headers=h,
            )
            assert r.status_code == 200

        logs_res = await client.get(f"/api/v1/audit/access-logs/{patient.id}")
        assert logs_res.status_code == 200
        logs = logs_res.json()
        assert len(logs) == 3

        for i, (expected_user, _, expected_purpose) in enumerate(inspections):
            assert logs[i]["user_id"] == expected_user
            assert logs[i]["purpose_code"] == expected_purpose

    async def test_default_purpose_code_is_clinical_review(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id="AIIA-AUDIT-003",
            study_title="Default Purpose Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-AUDIT-003",
            prakriti_type="PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()

        res = await client.get(f"/api/v1/patients/{patient.id}")
        assert res.status_code == 200

        logs_res = await client.get(f"/api/v1/audit/access-logs/{patient.id}")
        assert logs_res.status_code == 200
        logs = logs_res.json()
        assert len(logs) == 1
        assert logs[0]["purpose_code"] == "PURPOSE_CLINICAL_REVIEW"


@pytest.mark.asyncio
class TestExecutivePortfolioKPIAnalytics:

    async def test_portfolio_kpis_accurate_counts(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial_draft = ClinicalTrial(
            protocol_id="AIIA-KPI-DRAFT",
            study_title="Draft Protocol",
            status=TrialStatus.DRAFT,
        )
        trial_rec = ClinicalTrial(
            protocol_id="AIIA-KPI-REC",
            study_title="Recruiting Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add_all([trial_draft, trial_rec])
        await db_session.flush()

        p1 = TrialPatient(
            trial_id=trial_rec.id,
            usubjid="USJ-KPI-001",
            prakriti_type="VATA_PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        p2 = TrialPatient(
            trial_id=trial_rec.id,
            usubjid="USJ-KPI-002",
            prakriti_type="PITTA_KAPHA",
            baseline_agni="TIKSHNA",
            consent_status=ConsentStatus.WITHDRAWN,
        )
        db_session.add_all([p1, p2])
        await db_session.commit()

        ae_mild_payload = {
            "patient_id": str(p1.id),
            "severity": "MILD",
            "clinical_notes": "Mild headache",
            "ayurvedic_intervention": "Brahmi Vati",
            "concomitant_drugs": [],
            "reported_by": "dr_kpi",
        }
        ae_res = await client.post("/api/v1/safety/adverse-events", json=ae_mild_payload)
        assert ae_res.status_code == 201

        sae_payload = {
            "patient_id": str(p1.id),
            "severity": "LIFE_THREATENING",
            "clinical_notes": "Internal hemorrhage with dizziness",
            "ayurvedic_intervention": "Guduchi Ghana Vati",
            "concomitant_drugs": ["Aspirin"],
            "reported_by": "dr_kpi",
        }
        sae_res = await client.post("/api/v1/safety/adverse-events", json=sae_payload)
        assert sae_res.status_code == 201

        res = await client.get("/api/v1/analytics/portfolio-kpis?force_refresh=true")
        assert res.status_code == 200
        data = res.json()

        assert data["trial_portfolio"]["total_trials"] == 2
        assert data["trial_portfolio"]["DRAFT"] == 1
        assert data["trial_portfolio"]["RECRUITING"] == 1

        assert data["patient_metrics"]["total_enrolled"] == 2
        assert data["patient_metrics"]["active"] == 1
        assert data["patient_metrics"]["withdrawn"] == 1
        assert data["patient_metrics"]["prakriti_distribution"]["VATA_PITTA"] == 1
        assert data["patient_metrics"]["prakriti_distribution"]["PITTA_KAPHA"] == 1

        assert data["safety_kpis"]["total_adverse_events"] == 2
        assert data["safety_kpis"]["total_saes"] == 1
        assert data["safety_kpis"]["active_24h_clocks"] == 1
        assert data["safety_kpis"]["flagged_herb_drug_interactions"] == 1

        assert data["compliance_rate"] == 100.0
        assert data["cached"] is False

    async def test_kpi_caching_and_invalidation_on_new_sae(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial = ClinicalTrial(
            protocol_id="AIIA-CACHE-001",
            study_title="Caching Test Trial",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-CACHE-001",
            prakriti_type="TRIDOSHA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.commit()

        res1 = await client.get("/api/v1/analytics/portfolio-kpis?force_refresh=true")
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["cached"] is False
        assert data1["safety_kpis"]["total_saes"] == 0

        res2 = await client.get("/api/v1/analytics/portfolio-kpis")
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["cached"] is True
        assert data2["safety_kpis"]["total_saes"] == 0

        sae_payload = {
            "patient_id": str(patient.id),
            "severity": "HOSPITALIZATION",
            "clinical_notes": "Acute hepatitis with elevated liver enzymes",
            "ayurvedic_intervention": "Shankhapushpi",
            "concomitant_drugs": [],
            "reported_by": "dr_cache_test",
        }
        create_sae_res = await client.post("/api/v1/safety/adverse-events", json=sae_payload)
        assert create_sae_res.status_code == 201

        res3 = await client.get("/api/v1/analytics/portfolio-kpis")
        assert res3.status_code == 200
        data3 = res3.json()
        assert data3["cached"] is False
        assert data3["safety_kpis"]["total_saes"] == 1

        res4 = await client.get("/api/v1/analytics/portfolio-kpis")
        assert res4.status_code == 200
        data4 = res4.json()
        assert data4["cached"] is True
        assert data4["safety_kpis"]["total_saes"] == 1

    async def test_sae_breach_decreases_compliance_rate(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        from datetime import datetime, timedelta, timezone
        from app.models.clinical import AdverseEvent, AESeverity, AEStatus

        trial = ClinicalTrial(
            protocol_id="AIIA-BREACH-001",
            study_title="Breach Test Protocol",
            status=TrialStatus.RECRUITING,
        )
        db_session.add(trial)
        await db_session.flush()

        patient = TrialPatient(
            trial_id=trial.id,
            usubjid="USJ-BREACH-001",
            prakriti_type="PITTA",
            baseline_agni="SAMA",
            consent_status=ConsentStatus.OBTAINED,
        )
        db_session.add(patient)
        await db_session.flush()

        now = datetime.now(tz=timezone.utc)
        overdue_sae = AdverseEvent(
            patient_id=patient.id,
            severity=AESeverity.HOSPITALIZATION,
            is_serious=True,
            sae_clock_start=now - timedelta(hours=48),
            sla_deadline=now - timedelta(hours=24),
            status=AEStatus.OPEN,
            reported_by="dr_overdue",
            recorded_at=now - timedelta(hours=48),
        )
        active_sae = AdverseEvent(
            patient_id=patient.id,
            severity=AESeverity.LIFE_THREATENING,
            is_serious=True,
            sae_clock_start=now,
            sla_deadline=now + timedelta(hours=24),
            status=AEStatus.OPEN,
            reported_by="dr_active",
            recorded_at=now,
        )
        db_session.add_all([overdue_sae, active_sae])
        await db_session.commit()

        res = await client.get("/api/v1/analytics/portfolio-kpis?force_refresh=true")
        assert res.status_code == 200
        data = res.json()

        assert data["safety_kpis"]["total_saes"] == 2
        assert data["safety_kpis"]["active_24h_clocks"] == 1
        assert data["compliance_rate"] == 50.0

