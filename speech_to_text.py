import io
import tempfile
from typing import Optional, Union

import whisper


_model = None


def _get_model() -> whisper.Whisper:
    """
    Lazily load the Whisper model once.

    Use a small model for faster inference on CPUs and typical Streamlit Cloud hardware.
    """
    global _model
    if _model is None:
        # You can change to "base" or "small" depending on your hardware
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(audio_source: Union[bytes, str]) -> Optional[str]:
    """
    Transcribe audio into text using Whisper.

    Parameters
    ----------
    audio_source:
        - bytes: raw audio bytes from browser recorder / upload
        - str: path to an audio file on disk

    Returns
    -------
    transcript text or None if transcription fails.
    """
    try:
        model = _get_model()

        if isinstance(audio_source, bytes):
            # Write bytes to a temporary file for Whisper
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                tmp.write(audio_source)
                tmp.flush()
                result = model.transcribe(tmp.name)
        else:
            # Assume this is a file path
            result = model.transcribe(audio_source)

        return result.get("text", "").strip()
    except Exception:
        # In production you would log the exception details
        return None

