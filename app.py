
import base64
from typing import Any, Dict, List, Optional

import streamlit as st
try:
    from audio_recorder_streamlit import audio_recorder  # pyright: ignore[reportMissingImports]
except Exception:
    audio_recorder = None  # type: ignore[assignment]

from clinical_notes import generate_clinical_notes
from database import save_consultation_record
from entity_extraction import extract_medical_entities
from fhir_mapper import build_fhir_resources
from medicine_suggester import DISCLAIMER, suggest_medicines
from speech_to_text import transcribe_audio


def _init_session_state() -> None:
    if "page" not in st.session_state:
        st.session_state.page = "home"
    st.session_state.setdefault("patient_details", {})
    st.session_state.setdefault("transcript", "")
    st.session_state.setdefault("entities", {})
    st.session_state.setdefault("clinical_notes", "")
    st.session_state.setdefault("medicine_suggestions", {})
    st.session_state.setdefault("fhir_resources", {})
    st.session_state.setdefault("audio_bytes", None)
    st.session_state.setdefault("db_record_id", None)


def _mobile_first_css() -> None:
    st.markdown(
        """
        <style>
        .main {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
        button[kind="primary"], button[kind="secondary"] {
            min-height: 3rem;
            font-size: 1rem;
        }
        .block-button > button {
            width: 100% !important;
        }
        @media (max-width: 768px) {
            .main {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def navigate(page: str) -> None:
    st.session_state.page = page


def page_home() -> None:
    st.markdown(
        "<h2 style='text-align:center;'>Mobile-First Ambient AI Medical Scribe</h2>",
        unsafe_allow_html=True,
    )
    st.write(
        "Automatically convert doctor–patient conversations into structured "
        "FHIR-compliant medical records."
    )

    st.write("")
    col = st.container()
    with col:
        if st.button("Start Consultation", use_container_width=True):
            navigate("patient_details")


def page_patient_details() -> None:
    st.markdown("### Patient Details")

    pd = st.session_state.get("patient_details", {})
    name = st.text_input("Patient Name", value=pd.get("name", ""))
    gender = st.selectbox(
        "Gender",
        options=["", "Male", "Female", "Other"],
        index=["", "Male", "Female", "Other"].index(pd.get("gender", "") or ""),
    )
    age_or_dob = st.text_input(
        "Age or Birth Date",
        value=pd.get("age_or_birth_date", ""),
        placeholder="e.g., 32 or 1994-05-12",
    )
    chief_complaint = st.text_area(
        "Chief Complaint / Reason for Visit",
        value=pd.get("chief_complaint", ""),
    )

    if st.button("Continue to Consultation", use_container_width=True):
        st.session_state.patient_details = {
            "name": name.strip(),
            "gender": gender.strip(),
            "age_or_birth_date": age_or_dob.strip(),
            "chief_complaint": chief_complaint.strip(),
            # Convenience field: if it looks like a date, use it as birth_date in FHIR
            "birth_date": age_or_dob.strip() if "-" in age_or_dob else "",
        }
        navigate("consultation")


def page_consultation() -> None:
    st.markdown("### Consultation Recording")
    st.write("Provide the doctor–patient conversation audio.")

    tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])

    audio_bytes: Optional[bytes] = st.session_state.get("audio_bytes")

    with tab1:
        if audio_recorder is None:
            st.warning(
                "Audio recording is unavailable because `audio-recorder-streamlit` "
                "is not installed. Use the Upload Audio tab, or run: "
                "`pip install -r requirements.txt`."
            )
        else:
            st.write("Tap to start/stop recording (mobile and desktop supported).")
            recorded_audio = audio_recorder(
                text="Start / Stop Recording",
                icon_size="2x",
            )
            if recorded_audio is not None and len(recorded_audio) > 0:
                audio_bytes = recorded_audio

    with tab2:
        uploaded_file = st.file_uploader(
            "Upload Audio File",
            type=["wav", "mp3", "m4a"],
        )
        if uploaded_file is not None:
            audio_bytes = uploaded_file.read()

    if audio_bytes:
        st.session_state.audio_bytes = audio_bytes
        st.audio(audio_bytes, format="audio/wav")

    st.write("")
    if st.button("Run AI Pipeline", use_container_width=True):
        run_ai_pipeline()


def run_ai_pipeline() -> None:
    audio_bytes: Optional[bytes] = st.session_state.get("audio_bytes")
    if not audio_bytes:
        st.error("Please record or upload an audio file before running the AI pipeline.")
        return

    with st.spinner("Running speech-to-text..."):
        transcript, err = transcribe_audio(audio_bytes)
    if not transcript:
        st.error(
            f"**Speech-to-text failed.** {err or 'Please try again with a clearer recording.'}"
        )
        return

    st.session_state.transcript = transcript

    with st.spinner("Extracting medical entities..."):
        entities = extract_medical_entities(transcript)
    st.session_state.entities = entities

    with st.spinner("Generating clinical notes..."):
        clinical = generate_clinical_notes(
            transcript=transcript,
            entities=entities,
            patient=st.session_state.get("patient_details", {}),
        )
    st.session_state.clinical_notes = clinical

    with st.spinner("Suggesting medicines..."):
        medicine_suggestions = suggest_medicines(entities.get("symptoms", []))
    st.session_state.medicine_suggestions = medicine_suggestions

    with st.spinner("Creating FHIR resources..."):
        fhir_resources = build_fhir_resources(
            patient_details=st.session_state.get("patient_details", {}),
            entities=entities,
            clinical_notes=clinical,
            medicine_suggestions=medicine_suggestions,
        )
    st.session_state.fhir_resources = fhir_resources

    with st.spinner("Saving to database (if configured)..."):
        record_id = save_consultation_record(
            patient_details=st.session_state.get("patient_details", {}),
            transcript=transcript,
            entities=entities,
            clinical_notes=clinical,
            medicine_suggestions=medicine_suggestions,
            fhir_resources=fhir_resources,
        )
        st.session_state.db_record_id = record_id

    navigate("results")


def page_results() -> None:
    st.markdown("### Results Dashboard")

    transcript = st.session_state.get("transcript", "")
    entities = st.session_state.get("entities", {})
    clinical_notes = st.session_state.get("clinical_notes", "")
    medicine_suggestions = st.session_state.get("medicine_suggestions", {})
    fhir_resources = st.session_state.get("fhir_resources", {})

    st.markdown("#### Transcript")
    if transcript:
        st.text_area("Transcript", value=transcript, height=160)
    else:
        st.info("No transcript available yet.")

    st.markdown("#### Extracted Medical Entities")
    st.json(entities or {})

    st.markdown("#### AI Suggested Medicines")
    st.json(medicine_suggestions or {})
    st.caption(DISCLAIMER)

    st.markdown("#### Clinical Notes")
    if clinical_notes:
        st.text_area("Clinical Notes", value=clinical_notes, height=160)
    else:
        st.info("No clinical notes generated yet.")

    st.markdown("#### FHIR JSON Output")
    if fhir_resources:
        st.json(fhir_resources.get("bundle", fhir_resources))
    else:
        st.info("FHIR resources will appear here after running the AI pipeline.")

    st.markdown("#### Documentation Time Saved")
    st.write("**Documentation Time Without AI:** 5 minutes")
    st.write("**Documentation Time With AI:** 30 seconds")
    st.write("**Time Saved:** 90%")

    record_id = st.session_state.get("db_record_id")
    if record_id:
        st.success(f"Saved to database with ID: {record_id}")
    else:
        st.info(
            "MongoDB connection not configured or save skipped. "
            "Set `MONGODB_URI` to enable persistence."
        )

    if st.button("Start New Consultation", use_container_width=True):
        for key in [
            "patient_details",
            "transcript",
            "entities",
            "clinical_notes",
            "medicine_suggestions",
            "fhir_resources",
            "audio_bytes",
            "db_record_id",
        ]:
            st.session_state[key] = {} if isinstance(st.session_state.get(key), dict) else None
        navigate("home")


def main() -> None:
    st.set_page_config(
        page_title="Mobile-First Ambient AI Medical Scribe",
        layout="centered",
    )
    _init_session_state()
    _mobile_first_css()

    page = st.session_state.page
    if page == "home":
        page_home()
    elif page == "patient_details":
        page_patient_details()
    elif page == "consultation":
        page_consultation()
    elif page == "results":
        page_results()
    else:
        page_home()


if __name__ == "__main__":
    main()

