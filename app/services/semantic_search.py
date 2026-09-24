import math
import re
import uuid
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.clinical import AdverseEvent, TrialPatient

SEMANTIC_SYNONYMS: dict[str, list[str]] = {
    "concept_hepatic_jaundice": [
        "jaundice", "icterus", "scleral", "netra-peetata", "peeli", "peela", "peele",
        "aankhein", "yellow", "yellowing", "eyes", "hepatic", "liver", "hepatitis",
        "transaminases", "alt", "ast", "bilirubin", "hepatotoxicity", "tenderness",
        "hepatomegaly", "10023126"
    ],
    "concept_gastrointestinal_emesis": [
        "nausea", "vomiting", "vomit", "chhardi", "emesis", "hrillasa", "gastric",
        "stomach", "epigastric", "discomfort", "10028813"
    ],
    "concept_hemorrhagic_bleeding": [
        "bleeding", "hemorrhage", "raktapitta", "melena", "stool", "dark stool",
        "blood", "bruising", "hematoma", "petechiae"
    ],
    "concept_dermatologic_rash": [
        "rash", "kandu", "itching", "pruritus", "urticaria", "erythema", "dry skin",
        "eczema", "dermatitis"
    ],
    "concept_neurologic_headache": [
        "headache", "shirashoola", "cephalalgia", "dizziness", "bhrama", "vertigo", "confusion"
    ],
    "concept_metabolic_glycemic": [
        "hyperglycemia", "hypoglycemia", "glucose", "diabetes", "prameha", "hba1c"
    ],
}


def tokenize_text(text: str) -> list[str]:
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    tokens = [t.strip() for t in clean.split() if len(t.strip()) > 1]
    return tokens


def build_text_vector(text: str, extra_terms: Optional[list[str]] = None) -> dict[str, float]:
    vec: dict[str, float] = {}
    tokens = tokenize_text(text)
    full_lower = text.lower()

    if extra_terms:
        for et in extra_terms:
            full_lower += " " + et.lower()
            tokens.extend(tokenize_text(et))

    for t in tokens:
        vec[t] = vec.get(t, 0.0) + 1.0

    for i in range(len(tokens) - 1):
        bg = f"{tokens[i]}_{tokens[i+1]}"
        vec[bg] = vec.get(bg, 0.0) + 1.5

    for concept_id, keywords in SEMANTIC_SYNONYMS.items():
        hits = 0.0
        for kw in keywords:
            if " " in kw:
                if kw in full_lower:
                    hits += 2.0
            else:
                if kw in tokens or kw in full_lower:
                    hits += 1.0
        if hits > 0:
            vec[concept_id] = hits * 3.5

    return vec


def cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    dot = 0.0
    for k, val_a in vec_a.items():
        if k in vec_b:
            dot += val_a * vec_b[k]

    if dot <= 0.0:
        return 0.0

    norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
    norm_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return min(1.0, dot / (norm_a * norm_b))


async def find_similar_safety_cases(
    query_text: str,
    trial_id: Optional[uuid.UUID],
    db: AsyncSession,
    top_k: int = 5,
    threshold: float = 0.25,
) -> list[dict[str, Any]]:
    query_vec = build_text_vector(query_text)

    stmt = select(AdverseEvent).options(joinedload(AdverseEvent.patient))
    if trial_id is not None:
        stmt = stmt.join(TrialPatient, AdverseEvent.patient_id == TrialPatient.id).where(
            TrialPatient.trial_id == trial_id
        )

    res = await db.execute(stmt)
    adverse_events = res.scalars().all()

    ranked_cases: list[dict[str, Any]] = []

    for ae in adverse_events:
        case_content = (ae.clinical_notes or "") + " " + (ae.ayurvedic_intervention or "")
        extra_terms: list[str] = list(ae.concomitant_drugs or [])

        for med in (ae.coded_meddra_terms or []):
            if isinstance(med, dict):
                if "pt_name" in med:
                    extra_terms.append(med["pt_name"])
                if "soc_name" in med:
                    extra_terms.append(med["soc_name"])
                if "pt_code" in med:
                    extra_terms.append(str(med["pt_code"]))

        case_vec = build_text_vector(case_content, extra_terms=extra_terms)
        sim = cosine_similarity(query_vec, case_vec)

        if sim >= threshold:
            patient_usubjid = "UNKNOWN"
            patient_trial_id = None
            if ae.patient:
                patient_usubjid = ae.patient.usubjid
                patient_trial_id = str(ae.patient.trial_id)

            ranked_cases.append({
                "ae_id": str(ae.id),
                "patient_id": str(ae.patient_id),
                "usubjid": patient_usubjid,
                "trial_id": patient_trial_id,
                "severity": ae.severity.value,
                "is_serious": ae.is_serious,
                "clinical_notes": ae.clinical_notes,
                "ayurvedic_intervention": ae.ayurvedic_intervention,
                "concomitant_drugs": ae.concomitant_drugs,
                "coded_meddra_terms": ae.coded_meddra_terms,
                "similarity_score": round(sim, 4),
                "similarity_percentage": round(sim * 100.0, 1),
            })

    ranked_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    return ranked_cases[:top_k]
