import tempfile
from typing import Optional, Union

import whisper


# Magic bytes → file extension (Whisper/ffmpeg uses extension to decode)
_FORMAT_SIGS = (
    (b"RIFF", ".wav"),
    (b"\x1a\x45\xdf\xa3", ".webm"),
    (b"OggS", ".ogg"),
    (b"ID3", ".mp3"),
    (b"\xff\xfb", ".mp3"),
    (b"\xff\xfa", ".mp3"),
    (b"ftyp", ".m4a"),
)


def _suffix_for_bytes(data: bytes) -> str:
    """Pick file extension from magic bytes so ffmpeg can decode correctly."""
    for sig, ext in _FORMAT_SIGS:
        if data.startswith(sig):
            return ext
    return ".webm"  # fallback for browser recorders that may use webm


def _get_model() -> whisper.Whisper:
    """
    Lazily load the Whisper model once.

    Use a small model for faster inference on CPUs and typical Streamlit Cloud hardware.
    """
    global _model  # type: ignore[name-defined]
    try:
        _ = _model  # type: ignore[name-defined]
    except NameError:
        pass
    # Keep a module-level cache to avoid reloading on each call
    if " _whisper_model_cache" not in globals():
        globals()[" _whisper_model_cache"] = whisper.load_model("base")
    return globals()[" _whisper_model_cache"]


def transcribe_audio(audio_source: Union[bytes, str]) -> Optional[str]:
    """
    Transcribe audio into text using Whisper.

    Parameters
    ----------
    audio_source:
        - bytes: raw audio bytes from browser recorder / upload (WebM, WAV, MP3, etc.)
        - str: path to an audio file on disk

    Returns
    -------
    transcript text or None if transcription fails.
    """
    try:
        if isinstance(audio_source, bytes):
            suffix = _suffix_for_bytes(audio_source)
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
                tmp.write(audio_source)
                tmp.flush()
                model = _get_model()
                result = model.transcribe(tmp.name)
        else:
            model = _get_model()
            result = model.transcribe(audio_source)

        text = result.get("text", "").strip()
        return text if text else None
    except Exception:
        return None



