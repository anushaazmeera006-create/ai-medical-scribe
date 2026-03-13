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

### Speech-to-text (No Payment Option)

If you don’t want to pay for OpenAI, the app can run **offline speech-to-text** using **Vosk**.

1) Download a Vosk model (Hindi or multilingual) and unzip it somewhere on your PC.
2) Set the environment variable `VOSK_MODEL_PATH` to that folder.

PowerShell example:

```powershell
$env:VOSK_MODEL_PATH="C:\path\to\vosk-model-folder"
streamlit run app.py
```

**Note:** Offline STT works best with **WAV** recordings. (The app automatically uses offline STT when `OPENAI_API_KEY` is not set.)

### MongoDB Configuration (Optional)

Set these environment variables before running the app if you want to persist consultations:

- `MONGODB_URI` – MongoDB connection string
- `MONGODB_DB_NAME` – (optional) database name, default `ambient_medical_scribe`
- `MONGODB_COLLECTION_NAME` – (optional) collection name, default `consultations`






