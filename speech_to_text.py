import io
import tempfile
from typing import Optional, Union

import whisper
from pydub import AudioSegment


_model = None

# Magic bytes for format detection (first few bytes of file)
_FORMAT_SIGNATURES = (
    (b"RIFF", "wav"),
    (b"\x1a\x45\xdf\xa3", "webm"),  # EBML / WebM
    (b"OggS", "ogg"),
    (b"ID3", "mp3"),
    (b"\xff\xfb", "mp3"),  # MP3 frame sync
    (b"\xff\xfa", "mp3"),
    (b"fLaC", "flac"),
)


def _detect_format(audio_bytes: bytes) -> Optional[str]:
    """Detect audio format from magic bytes. Returns format for pydub (e.g. 'wav', 'webm')."""
    for sig, fmt in _FORMAT_SIGNATURES:
        if audio_bytes.startswith(sig):
            return fmt
    return None


def _bytes_to_wav(audio_bytes: bytes, hint_format: Optional[str] = None) -> bytes:
    """
    Convert arbitrary audio bytes to WAV using pydub.
    Tries detected format first, then common formats as fallback.
    """
    formats_to_try = []
    if hint_format:
        formats_to_try.append(hint_format)
    detected = _detect_format(audio_bytes)
    if detected and detected not in formats_to_try:
        formats_to_try.append(detected)
    for fmt in ("webm", "wav", "ogg", "mp3", "m4a", "mp4"):
        if fmt not in formats_to_try:
            formats_to_try.append(fmt)

    buf = io.BytesIO(audio_bytes)
    last_error: Optional[Exception] = None
    for fmt in formats_to_try:
        try:
            buf.seek(0)
            segment = AudioSegment.from_file(buf, format=fmt)
            out = io.BytesIO()
            segment.export(out, format="wav")
            out.seek(0)
            return out.read()
        except Exception as e:
            last_error = e
            continue
    if last_error:
        raise last_error
    raise ValueError("Could not decode audio with any supported format")


def _get_model() -> whisper.Whisper:
    """
    Lazily load the Whisper model once.

    Use a small model for faster inference on CPUs and typical Streamlit Cloud hardware.
    """
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


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
        model = _get_model()

        if isinstance(audio_source, bytes):
            # Normalize to WAV for Whisper (handles WebM, OGG, MP3, etc. from browser)
            wav_bytes = _bytes_to_wav(audio_source)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                tmp.write(wav_bytes)
                tmp.flush()
                result = model.transcribe(tmp.name)
        else:
            result = model.transcribe(audio_source)

        text = result.get("text", "").strip()
        return text if text else None
    except Exception:
        return None

