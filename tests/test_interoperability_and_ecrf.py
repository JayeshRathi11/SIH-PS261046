import csv
import io
import uuid
import zipfile
import xml.etree.ElementTree as ET
import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AlcoaAuditLedger
from tests.conftest import seed_trial_and_patient


class TestDynamicECRFStorageAndAudit:

    async def test_submit_ecrf_success_and_retrieval(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        visit_1_payload = {
            "visit_number": 1,
            "visit_name": "Day 0",
            "form_data": {
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "pulse_rate": 72,
                "current_agni": "SAMAGNI",
                "prakriti_scores": {"vata": 30, "pitta": 50, "kapha": 20},
                "doshic_imbalance": "Pitta Prakopa",
                "alt_enzyme": 24,
                "blood_glucose": 95,
                "dosage_compliance_pct": 100,
            },
            "modified_by": "dr_vaidya",
        }

        resp_v1 = await client.post(f"/api/v1/patients/{patient.id}/ecrf", json=visit_1_payload)
        assert resp_v1.status_code == 201
        data_v1 = resp_v1.json()
        assert data_v1["patient_id"] == str(patient.id)
        assert data_v1["visit_number"] == 1
        assert data_v1["visit_name"] == "Day 0"
        assert data_v1["form_data"]["current_agni"] == "SAMAGNI"
        assert data_v1["form_data"]["systolic_bp"] == 120

        visit_2_payload = {
            "visit_number": 2,
            "visit_name": "Day 14",
            "form_data": {
                "systolic_bp": 118,
                "diastolic_bp": 78,
                "pulse_rate": 70,
                "current_agni": "TIKSHNAGNI",
                "doshic_imbalance": "Shamana",
                "dosage_compliance_pct": 98,
            },
            "modified_by": "dr_vaidya",
        }

        resp_v2 = await client.post(f"/api/v1/patients/{patient.id}/ecrf", json=visit_2_payload)
        assert resp_v2.status_code == 201
        data_v2 = resp_v2.json()
        assert data_v2["visit_number"] == 2
        assert data_v2["form_data"]["current_agni"] == "TIKSHNAGNI"

        list_resp = await client.get(f"/api/v1/patients/{patient.id}/ecrf")
        assert list_resp.status_code == 200
        records = list_resp.json()
        assert len(records) == 2
        assert records[0]["visit_number"] == 1
        assert records[1]["visit_number"] == 2

    async def test_ecrf_audit_ledger_entry_and_chain_verification(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        payload = {
            "visit_number": 1,
            "visit_name": "Day 0",
            "form_data": {
                "systolic_bp": 122,
                "current_agni": "MANDAGNI",
            },
            "modified_by": "dr_vaidya",
        }

        resp = await client.post(f"/api/v1/patients/{patient.id}/ecrf", json=payload)
        assert resp.status_code == 201
        ecrf_id = resp.json()["id"]

        audit_stmt = select(AlcoaAuditLedger).where(AlcoaAuditLedger.entity_id == ecrf_id)
        audit_res = await db_session.execute(audit_stmt)
        audit_entry = audit_res.scalar_one_or_none()

        assert audit_entry is not None
        assert audit_entry.entity_name == "ecrf_records"
        assert audit_entry.modified_by == "dr_vaidya"
        assert audit_entry.field_changes["form_data"]["current_agni"] == "MANDAGNI"

        verify_resp = await client.get("/api/v1/audit/verify-chain")
        assert verify_resp.status_code == 200
        verify_data = verify_resp.json()
        assert verify_data["status"] == "VERIFIED_SECURE"
        assert verify_data["tampered_sequence_ids"] == []

    async def test_duplicate_visit_number_returns_409(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        payload = {
            "visit_number": 1,
            "visit_name": "Day 0",
            "form_data": {"systolic_bp": 120},
            "modified_by": "dr_vaidya",
        }

        resp_first = await client.post(f"/api/v1/patients/{patient.id}/ecrf", json=payload)
        assert resp_first.status_code == 201

        resp_dup = await client.post(f"/api/v1/patients/{patient.id}/ecrf", json=payload)
        assert resp_dup.status_code == 409
        assert "already exists" in resp_dup.json()["detail"]

    async def test_submit_ecrf_nonexistent_patient_returns_404(
        self, client: httpx.AsyncClient
    ):
        random_id = uuid.uuid4()
        payload = {
            "visit_number": 1,
            "visit_name": "Day 0",
            "form_data": {"systolic_bp": 120},
            "modified_by": "dr_vaidya",
        }
        resp = await client.post(f"/api/v1/patients/{random_id}/ecrf", json=payload)
        assert resp.status_code == 404


class TestCdiscSdtmPackaging:

    async def test_export_cdisc_sdtm_zip_structure_and_content(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        trial, patient = await seed_trial_and_patient(db_session)

        await client.post(
            f"/api/v1/patients/{patient.id}/ecrf",
            json={
                "visit_number": 1,
                "visit_name": "Day 0",
                "form_data": {
                    "systolic_bp": 125,
                    "diastolic_bp": 82,
                    "pulse_rate": 74,
                },
                "modified_by": "dr_vaidya",
            },
        )

        await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "HOSPITALIZATION",
                "clinical_notes": "Patient presented with netra-peetata and melena.",
                "ayurvedic_intervention": "Guduchi Ghanvati",
                "concomitant_drugs": ["Aspirin"],
                "reported_by": "dr_vaidya",
            },
        )

        resp = await client.get(f"/api/v1/export/cdisc-sdtm/{trial.id}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"
        assert f"CDISC_SDTM_{trial.id}.zip" in resp.headers["content-disposition"]

        zip_bytes = resp.content
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            file_names = set(zf.namelist())
            assert "dm.csv" in file_names
            assert "vs.csv" in file_names
            assert "ae.csv" in file_names
            assert "define.xml" in file_names

            dm_content = zf.read("dm.csv").decode("utf-8")
            dm_reader = list(csv.reader(io.StringIO(dm_content)))
            assert dm_reader[0] == ["STUDYID", "DOMAIN", "USUBJID", "SUBJID", "AGE", "SEX", "ARMCD", "COUNTRY"]
            assert len(dm_reader) >= 2
            assert dm_reader[1][0] == trial.protocol_id
            assert dm_reader[1][1] == "DM"
            assert dm_reader[1][2] == patient.usubjid

            vs_content = zf.read("vs.csv").decode("utf-8")
            vs_reader = list(csv.reader(io.StringIO(vs_content)))
            assert vs_reader[0] == ["STUDYID", "DOMAIN", "USUBJID", "VSSEQ", "VSTESTCD", "VSTEST", "VSORRES", "VSORRESU", "VISITNUM", "VISIT"]
            tests_found = {row[4] for row in vs_reader[1:]}
            assert "SYSBP" in tests_found
            assert "DIABP" in tests_found
            assert "PULSE" in tests_found

            ae_content = zf.read("ae.csv").decode("utf-8")
            ae_reader = list(csv.reader(io.StringIO(ae_content)))
            assert ae_reader[0] == ["STUDYID", "DOMAIN", "USUBJID", "AESEQ", "AETERM", "AEDECOD", "AESEV", "AESER", "AESTDTC"]
            assert len(ae_reader) >= 2
            assert ae_reader[1][1] == "AE"
            assert ae_reader[1][7] == "Y"

            define_content = zf.read("define.xml").decode("utf-8")
            root = ET.fromstring(define_content)
            assert root.tag.endswith("ODM")
            item_groups = root.findall(".//{http://www.cdisc.org/ns/odm/v1.3}ItemGroupDef")
            ig_names = {ig.attrib.get("Name") for ig in item_groups}
            assert "DM" in ig_names
            assert "VS" in ig_names
            assert "AE" in ig_names

    async def test_export_cdisc_sdtm_nonexistent_trial_returns_404(
        self, client: httpx.AsyncClient
    ):
        random_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/export/cdisc-sdtm/{random_id}")
        assert resp.status_code == 404


class TestHl7FhirR4Serialization:

    async def test_export_fhir_bundle_structure_and_resources(
        self, client: httpx.AsyncClient, db_session: AsyncSession
    ):
        _, patient = await seed_trial_and_patient(db_session)

        await client.post(
            f"/api/v1/patients/{patient.id}/ecrf",
            json={
                "visit_number": 1,
                "visit_name": "Day 0",
                "form_data": {
                    "systolic_bp": 128,
                    "diastolic_bp": 84,
                    "pulse_rate": 76,
                    "alt_enzyme": 32,
                    "blood_glucose": 105,
                    "current_agni": "VISHAMAGNI",
                },
                "modified_by": "dr_vaidya",
            },
        )

        await client.post(
            "/api/v1/safety/adverse-event",
            json={
                "patient_id": str(patient.id),
                "severity": "HOSPITALIZATION",
                "clinical_notes": "Patient presented with netra-peetata and nausea.",
                "ayurvedic_intervention": "Guduchi Kwath",
                "concomitant_drugs": ["Aspirin"],
                "reported_by": "dr_vaidya",
            },
        )

        resp = await client.get(f"/api/v1/export/fhir-bundle/{patient.id}")
        assert resp.status_code == 200
        bundle = resp.json()

        assert bundle["resourceType"] == "Bundle"
        assert bundle["type"] == "collection"
        assert "entry" in bundle
        assert len(bundle["entry"]) >= 4

        resource_types = [entry["resource"]["resourceType"] for entry in bundle["entry"]]
        assert "Patient" in resource_types
        assert "Observation" in resource_types
        assert "AdverseEvent" in resource_types

        patient_res = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient")
        assert patient_res["id"] == str(patient.id)
        assert patient_res["identifier"][0]["value"] == patient.usubjid
        extension_urls = {ext["url"] for ext in patient_res.get("extension", [])}
        assert "https://ayush.gov.in/fhir/StructureDefinition/prakriti-type" in extension_urls
        assert "https://ayush.gov.in/fhir/StructureDefinition/baseline-agni" in extension_urls

        obs_resources = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation"]
        loinc_codes = set()
        for obs in obs_resources:
            for coding in obs.get("code", {}).get("coding", []):
                loinc_codes.add(coding.get("code"))
        assert "8480-6" in loinc_codes
        assert "8462-4" in loinc_codes
        assert "8867-4" in loinc_codes
        assert "1742-6" in loinc_codes
        assert "2339-0" in loinc_codes
        assert "AYUSH-AGNI-01" in loinc_codes

        ae_res = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "AdverseEvent")
        assert ae_res["actuality"] == "actual"
        assert ae_res["subject"]["reference"] == f"Patient/{patient.id}"
        meddra_codes = {c["code"] for c in ae_res.get("event", {}).get("coding", [])}
        assert "10023126" in meddra_codes

    async def test_export_fhir_bundle_nonexistent_patient_returns_404(
        self, client: httpx.AsyncClient
    ):
        random_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/export/fhir-bundle/{random_id}")
        assert resp.status_code == 404
