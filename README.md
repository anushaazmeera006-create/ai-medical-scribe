## Mobile-First Ambient AI Medical Scribe

This Streamlit app converts doctor–patient conversations into structured clinical notes and FHIR-like healthcare data, with optional MongoDB persistence.

### Features

- **Mobile-first UI** that works on phones and desktops
- **Audio recording or upload** for consultation audio
- **Whisper-based speech-to-text** (multilingual → English, works offline)
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

### Speech-to-text (Free, Offline)

This app now uses **`faster-whisper`** locally. No OpenAI key or payments needed.

1) Install dependencies:

```bash
pip install -r requirements.txt
```

2) On first run, `faster-whisper` will download a Whisper model (default: `small`).
3) All doctor–patient audio (Hindi + English mixed) is automatically **translated to English text**.

Optional: to use a smaller / faster model (less accurate), set:

```powershell
$env:FAST_WHISPER_MODEL_SIZE="tiny"   # or "base", "small", "medium"
streamlit run app.py
```

### MongoDB Configuration (Optional)

Set these environment variables before running the app if you want to persist consultations:

- `MONGODB_URI` – MongoDB connection string
- `MONGODB_DB_NAME` – (optional) database name, default `ambient_medical_scribe`
- `MONGODB_COLLECTION_NAME` – (optional) collection name, default `consultations`








