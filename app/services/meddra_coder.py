from typing import List, Dict
import re

MEDDRA_MAP = {
    "peeli aankhein": {"pt": "10023126", "term": "Jaundice ocular", "soc": "Eye disorders"},
    "yellowing of sclera": {"pt": "10023126", "term": "Jaundice ocular", "soc": "Eye disorders"},
    "netra-peetata": {"pt": "10023126", "term": "Jaundice ocular", "soc": "Eye disorders"},
    "pet me jalan": {"pt": "10018884", "term": "Heartburn", "soc": "GI disorders"},
    "amlapitta": {"pt": "10018884", "term": "Heartburn", "soc": "GI disorders"},
    "burning epigastrium": {"pt": "10018884", "term": "Heartburn", "soc": "GI disorders"},
    "nausea": {"pt": "10028813", "term": "Nausea", "soc": "GI disorders"},
    "chhardi": {"pt": "10028813", "term": "Nausea", "soc": "GI disorders"},
    "ulti": {"pt": "10028813", "term": "Nausea", "soc": "GI disorders"},
    "yakrit shotha": {"pt": "10019699", "term": "Hepatosplenomegaly", "soc": "Hepatobiliary disorders"},
    "hepatic tenderness": {"pt": "10019699", "term": "Hepatosplenomegaly", "soc": "Hepatobiliary disorders"},
    "melena": {"pt": "10027175", "term": "Melaena", "soc": "GI disorders"},
    "dark stool": {"pt": "10027175", "term": "Melaena", "soc": "GI disorders"},
    "raktapitta": {"pt": "10027175", "term": "Melaena", "soc": "GI disorders"},
}

def extract_meddra_terms(clinical_notes: str) -> List[Dict]:
    """Return list of matching MedDRA entries from free‑text notes.
    Matching is case‑insensitive and looks for exact substrings defined in
    ``MEDDRA_MAP``. Overlapping terms are all returned.
    """
    if not clinical_notes:
        return []
    lowered = clinical_notes.lower()
    results: List[Dict] = []
    for phrase, info in MEDDRA_MAP.items():
        if phrase in lowered:
            results.append({
                "phrase": phrase,
                "pt_code": info["pt"],
                "preferred_term": info["term"],
                "soc": info["soc"],
            })
    return results
