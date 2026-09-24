import uuid
import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AlcoaAuditLedger
from app.services.herb_matrix import check_herb_drug_interactions
from app.services.meddra_coder import extract_meddra_terms
from tests.conftest import seed_trial_and_patient


class TestHerbDrugConflictEngine:

    def test_guduchi_and_aspirin_critical_conflict(self):
        conflicts = check_herb_drug_interactions("Guduchi Ghanvati", ["Aspirin", "Paracetamol"])
        assert len(conflicts) == 1
        assert conflicts[0]["herb"] == "Guduchi"
        assert conflicts[0]["drug"] == "Aspirin"
        assert conflicts[0]["severity"] == "CRITICAL"
        assert "Antiplatelet potentiation" in conflicts[0]["description"]

    def test_guggulu_and_warfarin_critical_conflict(self):
        conflicts = check_herb_drug_interactions("Yograj Guggulu", ["Warfarin"])
        assert len(conflicts) == 1
        assert conflicts[0]["herb"] == "Guggulu"
        assert conflicts[0]["drug"] == "Warfarin"
        assert conflicts[0]["severity"] == "CRITICAL"

    def test_safe_non_interacting_drugs_return_empty(self):
        conflicts = check_herb_drug_interactions("Ashwagandha Churna", ["Paracetamol", "Amoxicillin"])
        assert conflicts == []


class TestMeddraCodingEngine:

    def test_mixed_clinical_notes_extraction(self):
        notes = "Patient presented with netra-peetata and severe nausea after intervention."
        terms = extract_meddra_terms(notes)
        assert len(terms) == 2
        pt_codes = {t["pt_code"] for t in terms}
        pref_terms = {t["preferred_term"] for t in terms}
        assert "10023126" in pt_codes
        assert "10028813" in pt_codes
        assert "Jaundice ocular" in pref_terms
        assert "Nausea" in pref_terms

    def test_colloquial_ayurvedic_terms_extraction(self):
        notes = "Reported burning epigastrium with amlapitta and dark stool."
        terms = extract_meddra_terms(notes)
        pt_codes = {t["pt_code"] for t in terms}
        assert "10018884" in pt_codes
        assert "10027175" in pt_codes

    def test_notes_without_matches_return_empty(self):
        terms = extract_meddra_terms("Patient is resting comfortably without pain.")
        assert terms == []


class TestEnrichedSaeLoggingAndAuditChaining:

    async def test_sae_creates_enriched_record_and_valid_audit_chain(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        payload = {
            "patient_id": str(patient.id),
            "severity": "HOSPITALIZATION",
            "clinical_notes": "Patient presented with netra-peetata and dark stool.",
            "ayurvedic_intervention": "Guduchi Rasayana",
            "concomitant_drugs": ["Aspirin"],
            "reported_by": "dr_vaidya",
        }

        resp = await client.post("/api/v1/safety/adverse-event", json=payload)
        assert resp.status_code == 201
        data = resp.json()

        assert data["is_serious"] is True
        assert data["sae_clock_start"] is not None
        assert data["sla_deadline"] is not None
        assert data["has_conflict"] is True
        assert data["form_ct16_available"] is True
        assert len(data["herb_drug_conflicts"]) == 1
        assert data["herb_drug_conflicts"][0]["severity"] == "CRITICAL"
        assert len(data["coded_meddra_terms"]) == 2

        ae_id = data["id"]
        audit_stmt = select(AlcoaAuditLedger).where(AlcoaAuditLedger.entity_id == ae_id)
        audit_result = await db_session.execute(audit_stmt)
        audit_entry = audit_result.scalar_one_or_none()

        assert audit_entry is not None
        assert audit_entry.field_changes["has_conflict"] is True
        assert audit_entry.field_changes["herb_drug_conflicts"][0]["drug"] == "Aspirin"
        assert len(audit_entry.field_changes["coded_meddra_terms"]) == 2

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["status"] == "VERIFIED_SECURE"
        assert verify_data["tampered_sequence_ids"] == []
        assert verify_data["total_blocks"] >= 1


class TestCdscoFormCt16PdfEndpoint:

    async def test_sae_generates_valid_pdf(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        post_resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "LIFE_THREATENING",
                "clinical_notes": "Acute upper GI bleeding, melena and nausea reported.",
                "ayurvedic_intervention": "Guduchi Kwath",
                "concomitant_drugs": ["Aspirin", "Clopidogrel"],
                "reported_by": "dr_patel",
            },
        )
        assert post_resp.status_code == 201
        ae_id = post_resp.json()["id"]

        report_resp = await client.get(f"/api/v1/safety/reports/ct16/{ae_id}")
        assert report_resp.status_code == 200
        assert report_resp.headers["content-type"] == "application/pdf"
        assert report_resp.headers["content-disposition"] == f"attachment; filename=Form_CT16_{ae_id}.pdf"
        assert report_resp.content.startswith(b"%PDF-")
        assert len(report_resp.content) > 1000

    async def test_mild_adverse_event_ct16_returns_400(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        post_resp = await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "MILD",
                "clinical_notes": "Mild transient pruritus.",
                "ayurvedic_intervention": "Ashwagandha Tablet",
                "concomitant_drugs": ["Paracetamol"],
                "reported_by": "dr_patel",
            },
        )
        assert post_resp.status_code == 201
        ae_id = post_resp.json()["id"]

        report_resp = await client.get(f"/api/v1/safety/reports/ct16/{ae_id}")
        assert report_resp.status_code == 400
        assert report_resp.json()["detail"] == "Form CT-16 is only generated for Serious Adverse Events (SAE)"

    async def test_nonexistent_adverse_event_returns_404(
        self, client: httpx.AsyncClient
    ):
        random_id = uuid.uuid4()
        report_resp = await client.get(f"/api/v1/safety/reports/ct16/{random_id}")
        assert report_resp.status_code == 404
        assert report_resp.json()["detail"] == "Adverse event not found"
