from typing import Dict, List


SYMPTOM_TO_MEDICINE_MAP: Dict[str, List[str]] = {
    "fever": ["Paracetamol"],
    "headache": ["Ibuprofen", "Paracetamol"],
    "cold": ["Cetirizine"],
}


DISCLAIMER = (
    "For demonstration purposes only. Final prescription must be verified by a doctor."
)


def suggest_medicines(symptoms: List[str]) -> Dict[str, List[str]]:
    """
    Return a mapping from symptom to suggested medicines.
    """
    suggestions: Dict[str, List[str]] = {}
    for s in symptoms:
        meds = SYMPTOM_TO_MEDICINE_MAP.get(s.lower())
        if meds:
            suggestions[s] = meds
    return suggestions

