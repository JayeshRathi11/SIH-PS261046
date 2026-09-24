import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import TrialPatient, ECRFRecord, AdverseEvent, ConsentStatus


async def generate_patient_fhir_bundle(patient_id: uuid.UUID, db: AsyncSession) -> Optional[Dict[str, Any]]:
    stmt = (
        select(TrialPatient)
        .options(
            selectinload(TrialPatient.ecrf_records),
            selectinload(TrialPatient.adverse_events),
        )
        .where(TrialPatient.id == patient_id)
    )
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    if patient is None or patient.consent_status == ConsentStatus.WITHDRAWN:
        return None

    bundle_id = str(uuid.uuid4())
    now_str = datetime.now(tz=timezone.utc).isoformat()

    entries: List[Dict[str, Any]] = []

    patient_res = {
        "resourceType": "Patient",
        "id": str(patient.id),
        "identifier": [
            {
                "system": "https://healthid.ndhm.gov.in",
                "value": patient.usubjid,
            }
        ],
        "active": True,
        "gender": getattr(patient, "sex", "unknown").lower() if getattr(patient, "sex", None) else "unknown",
        "extension": [
            {
                "url": "https://ayush.gov.in/fhir/StructureDefinition/prakriti-type",
                "valueString": patient.prakriti_type or "Unknown",
            },
            {
                "url": "https://ayush.gov.in/fhir/StructureDefinition/baseline-agni",
                "valueString": patient.baseline_agni or "Unknown",
            },
        ],
    }
    entries.append({"resource": patient_res})

    for ecrf in patient.ecrf_records:
        form = ecrf.form_data or {}
        dt = ecrf.recorded_at.isoformat() if ecrf.recorded_at else now_str

        if "systolic_bp" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8480-6",
                            "display": "Systolic blood pressure",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueQuantity": {
                        "value": float(form["systolic_bp"]),
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                }
            })

        if "diastolic_bp" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8462-4",
                            "display": "Diastolic blood pressure",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueQuantity": {
                        "value": float(form["diastolic_bp"]),
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]",
                    },
                }
            })

        if "pulse_rate" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs",
                            "display": "Vital Signs",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "8867-4",
                            "display": "Heart rate",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueQuantity": {
                        "value": float(form["pulse_rate"]),
                        "unit": "beats/min",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min",
                    },
                }
            })

        if "alt_enzyme" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "1742-6",
                            "display": "Alanine aminotransferase",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueQuantity": {
                        "value": float(form["alt_enzyme"]),
                        "unit": "U/L",
                        "system": "http://unitsofmeasure.org",
                        "code": "U/L",
                    },
                }
            })

        if "blood_glucose" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory",
                            "display": "Laboratory",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": "2339-0",
                            "display": "Glucose [Mass/volume] in Blood",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueQuantity": {
                        "value": float(form["blood_glucose"]),
                        "unit": "mg/dL",
                        "system": "http://unitsofmeasure.org",
                        "code": "mg/dL",
                    },
                }
            })

        if "current_agni" in form:
            entries.append({
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "https://ayush.gov.in/fhir/CodeSystem/observation-category",
                            "code": "ayurvedic-phenotype",
                            "display": "Ayurvedic Phenotype",
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "https://ayush.gov.in/fhir/CodeSystem/biomarkers",
                            "code": "AYUSH-AGNI-01",
                            "display": "Ayurvedic Agni State",
                        }]
                    },
                    "subject": {"reference": f"Patient/{patient.id}"},
                    "effectiveDateTime": dt,
                    "valueString": str(form["current_agni"]),
                }
            })

    for ae in patient.adverse_events:
        ae_coding = []
        if ae.coded_meddra_terms and isinstance(ae.coded_meddra_terms, list):
            for t in ae.coded_meddra_terms:
                ae_coding.append({
                    "system": "http://www.meddra.org",
                    "code": str(t.get("pt_code", "UNKNOWN")),
                    "display": str(t.get("preferred_term", "Adverse Event")),
                })
        if not ae_coding:
            ae_coding.append({
                "system": "http://snomed.info/sct",
                "code": "281647001",
                "display": ae.clinical_notes or "Adverse Event",
            })

        entries.append({
            "resource": {
                "resourceType": "AdverseEvent",
                "id": str(ae.id),
                "actuality": "actual",
                "subject": {"reference": f"Patient/{patient.id}"},
                "date": ae.recorded_at.isoformat() if ae.recorded_at else now_str,
                "severity": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/adverse-event-severity",
                        "code": ae.severity.value.lower(),
                        "display": ae.severity.value,
                    }]
                },
                "seriousness": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/adverse-event-seriousness",
                        "code": "serious" if ae.is_serious else "non-serious",
                        "display": "Serious" if ae.is_serious else "Non-Serious",
                    }]
                },
                "event": {"coding": ae_coding},
            }
        })

    return {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": "collection",
        "timestamp": now_str,
        "entry": entries,
    }
