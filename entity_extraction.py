import re
from typing import Dict, List, Optional


SYMPTOM_KEYWORDS = {
    "fever": ["fever", "bukhar", "bukhār", "high temperature", "temperature"],
    "headache": ["headache", "sir dard", "sirdard", "sardard", "migraine"],
    "cold": ["cold", "sardi", "zukam", "zukaam", "runny nose", "blocked nose"],
    "cough": ["cough", "khansi", "khansi ho rahi", "khasi"],
    "sore throat": ["sore throat", "gale me dard", "throat pain"],
    "body pain": ["body pain", "body ache", "sarir dard", "body is paining"],
}

MEDICATION_KEYWORDS = {
    "paracetamol": ["paracetamol", "calpol", "crocin", "dolo", "dolo 650"],
    "ibuprofen": ["ibuprofen", "brufen"],
    "cetirizine": ["cetirizine", "cetzine", "zyncet"],
    "cough syrup": [
        "cough syrup",
        "benadryl",
        "as-coril",
        "as coril",
        "torex",
        "grilinctus",
    ],
}


def _find_keywords(text: str, keyword_map: Dict[str, List[str]]) -> List[str]:
    text_lower = text.lower()
    found = set()
    for canonical, variants in keyword_map.items():
        for v in variants:
            if v in text_lower:
                found.add(canonical)
                break
    return sorted(found)


def _extract_duration(text: str) -> Optional[str]:
    """
    Extract simple duration patterns like:
    - "3 din se"
    - "3 days"
    - "2 weeks"
    - "1 month"
    """
    patterns = [
        r"(\d+)\s*(din|day|days|week|weeks|month|months)\s*(se|since)?",
        r"for\s+(\d+)\s*(day|days|week|weeks|month|months)",
    ]
    text_lower = text.lower()
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0).strip()
    return None


def extract_medical_entities(transcript: str) -> Dict[str, List[str]]:
    """
    Very simple rule-based entity extraction for demo purposes.
    """
    symptoms = _find_keywords(transcript, SYMPTOM_KEYWORDS)
    medications = _find_keywords(transcript, MEDICATION_KEYWORDS)
    duration = _extract_duration(transcript)

    # For this demo, treat the first symptom as "disease" label if none is explicitly given.
    disease = symptoms[0] if symptoms else ""

    return {
        "symptoms": symptoms,
        "disease": [disease] if disease else [],
        "duration": [duration] if duration else [],
        "medications": medications,
    }

