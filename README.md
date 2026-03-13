## Mobile-First Ambient AI Medical Scribe

This Streamlit app converts doctor–patient conversations into structured clinical notes and FHIR-like healthcare data, with optional MongoDB persistence.

### Features

- **Mobile-first UI** that works on phones and desktops
- **Audio recording or upload** for consultation audio
- **Whisper-based speech-to-text** (Hindi + English mixed speech)
- **Rule-based medical entity extraction**
- **Clinical note generation**
- **Medicine suggestions** with disclaimer
- **FHIR-style JSON mapping** (Patient, Encounter, Condition, Observation, MedicationRequest, Bundle)
- **MongoDB storage** for end-to-end records

### Project Structure

- `app.py` – Streamlit app with multi-page workflow
- `speech_to_text.py` – Whisper integration
- `entity_extraction.py` – Simple rule-based NLP
- `clinical_notes.py` – Clinical summary generator
- `medicine_suggester.py` – Symptom-to-medicine mapping
- `fhir_mapper.py` – FHIR JSON resource creation
- `database.py` – MongoDB persistence helpers
- `requirements.txt` – Python dependencies

### Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

**Note:** Speech-to-text uses the OpenAI Whisper API directly and does **not** require `ffmpeg`/`pydub` locally.

### MongoDB Configuration (Optional)

Set these environment variables before running the app if you want to persist consultations:

- `MONGODB_URI` – MongoDB connection string
- `MONGODB_DB_NAME` – (optional) database name, default `ambient_medical_scribe`
- `MONGODB_COLLECTION_NAME` – (optional) collection name, default `consultations`



