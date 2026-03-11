from datetime import datetime
from typing import Any, Dict, List


def build_fhir_resources(
    patient_details: Dict[str, Any],
    entities: Dict[str, List[str]],
    clinical_notes: str,
    medicine_suggestions: Dict[str, List[str]],
) -> Dict[str, Any]:
    """
    Create a minimal set of FHIR-like resources for demo purposes.
    """
    patient_id = "demo-patient-001"
    encounter_id = "demo-encounter-001"

    patient_resource = {
        "resourceType": "Patient",
        "id": patient_id,
        "name": [
            {
                "text": patient_details.get("name"),
            }
        ],
        "gender": (patient_details.get("gender") or "").lower() or None,
        "birthDate": patient_details.get("birth_date"),
        "extension": [
            {
                "url": "http://example.org/fhir/StructureDefinition/chief-complaint",
                "valueString": patient_details.get("chief_complaint"),
            }
        ],
    }

    encounter_resource = {
        "resourceType": "Encounter",
        "id": encounter_id,
        "status": "finished",
        "class": {"code": "AMB", "display": "Ambulatory"},
        "subject": {"reference": f"Patient/{patient_id}"},
        "period": {
            "start": datetime.utcnow().isoformat() + "Z",
        },
    }

    conditions = []
    for disease in entities.get("disease", []):
        if not disease:
            continue
        conditions.append(
            {
                "resourceType": "Condition",
                "code": {"text": disease},
                "subject": {"reference": f"Patient/{patient_id}"},
            }
        )

    observations = []
    for symptom in entities.get("symptoms", []):
        observations.append(
            {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": symptom},
                "subject": {"reference": f"Patient/{patient_id}"},
                "encounter": {"reference": f"Encounter/{encounter_id}"},
            }
        )

    medication_requests = []
    for symptom, meds in medicine_suggestions.items():
        for med in meds:
            medication_requests.append(
                {
                    "resourceType": "MedicationRequest",
                    "status": "active",
                    "intent": "proposal",
                    "medicationCodeableConcept": {"text": med},
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "reasonReference": [{"display": symptom}],
                }
            )

    clinical_impression = {
        "resourceType": "ClinicalImpression",
        "status": "completed",
        "description": clinical_notes,
        "subject": {"reference": f"Patient/{patient_id}"},
        "encounter": {"reference": f"Encounter/{encounter_id}"},
    }

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {"resource": patient_resource},
            {"resource": encounter_resource},
            *({"resource": r} for r in conditions),
            *({"resource": r} for r in observations),
            *({"resource": r} for r in medication_requests),
            {"resource": clinical_impression},
        ],
    }

    return {
        "patient": patient_resource,
        "encounter": encounter_resource,
        "conditions": conditions,
        "observations": observations,
        "medication_requests": medication_requests,
        "bundle": bundle,
    }

