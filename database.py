import os
from datetime import datetime
from typing import Any, Dict, Optional

from pymongo import MongoClient
from pymongo.collection import Collection


def _get_mongo_uri() -> Optional[str]:
    """
    Read MongoDB connection string from environment.
    """
    return os.getenv("MONGODB_URI")


def get_collection() -> Optional[Collection]:
    """
    Return a MongoDB collection handle or None if connection is not configured.
    """
    uri = _get_mongo_uri()
    if not uri:
        return None

    client = MongoClient(uri)
    db_name = os.getenv("MONGODB_DB_NAME", "ambient_medical_scribe")
    collection_name = os.getenv("MONGODB_COLLECTION_NAME", "consultations")
    db = client[db_name]
    return db[collection_name]


def save_consultation_record(
    patient_details: Dict[str, Any],
    transcript: str,
    entities: Dict[str, Any],
    clinical_notes: str,
    medicine_suggestions: Dict[str, Any],
    fhir_resources: Dict[str, Any],
) -> Optional[str]:
    """
    Persist a single consultation to MongoDB.
    Returns the inserted document ID as string, or None if DB is not configured.
    """
    collection = get_collection()
    if collection is None:
        return None

    doc = {
        "patient_details": patient_details,
        "transcript": transcript,
        "entities": entities,
        "clinical_notes": clinical_notes,
        "medicine_suggestions": medicine_suggestions,
        "fhir": fhir_resources,
        "created_at": datetime.utcnow(),
    }

    result = collection.insert_one(doc)
    return str(result.inserted_id)

