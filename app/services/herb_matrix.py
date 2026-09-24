import json, os
from typing import List, Dict

def load_matrix() -> List[Dict]:
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'herb_matrix.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)['rules']

RULES = load_matrix()

def check_herb_drug_interactions(ayurvedic_intervention: str, concomitant_drugs: List[str]) -> List[Dict]:
    res = []
    ai = ayurvedic_intervention.lower() if ayurvedic_intervention else ''
    drugs_lower = [d.lower() for d in concomitant_drugs]
    for rule in RULES:
        herb = rule['herb'].lower()
        if herb in ai:
            for drug in rule['drugs']:
                d_target = drug.lower()
                if any(d_target in d for d in drugs_lower):
                    res.append({
                        'herb': rule['herb'],
                        'drug': drug,
                        'severity': rule['severity'],
                        'description': rule['description']
                    })
    return res
