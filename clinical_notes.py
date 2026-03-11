from typing import Dict, List, Optional


def generate_clinical_notes(
    transcript: str,
    entities: Dict[str, List[str]],
    patient: Dict[str, str],
) -> str:
    """
    Create a concise clinical note from transcript, entities, and patient details.
    """
    name = patient.get("name") or "The patient"

    symptoms = entities.get("symptoms") or []
    duration_list = entities.get("duration") or []
    meds = entities.get("medications") or []

    parts = []

    if symptoms:
        parts.append(
            f"{name} reports " + ", ".join(symptoms) + ("." if len(symptoms) == 1 else ".")
        )

    if duration_list:
        parts.append(f"Symptoms have been present for {duration_list[0]}.")

    if meds:
        parts.append(
            "Currently taking "
            + ", ".join(meds)
            + " for symptom relief."
        )

    if not parts:
        parts.append(
            "Clinical summary could not be fully generated from the available transcript. "
            "Please review and complete manually."
        )

    note = " ".join(parts)
    return note.strip()

