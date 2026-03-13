import tempfile
import io
from typing import Optional, Tuple, Union

from openai import OpenAI


# Magic bytes → file extension (helps OpenAI infer format)
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
    """Pick file extension from magic bytes."""
    for sig, ext in _FORMAT_SIGS:
        if data.startswith(sig):
            return ext
    return ".webm"  # fallback for browser recorders that may use webm


def _get_client() -> OpenAI:
    # Module-level cache avoids re-creating the client on each call.
    if "_openai_client_cache" not in globals():
        globals()["_openai_client_cache"] = OpenAI()
    return globals()["_openai_client_cache"]


def transcribe_audio(audio_source: Union[bytes, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio into text using OpenAI Whisper API.

    Returns
    -------
    (transcript, error_message). On success: (text, None). On failure: (None, error_str).
    """
    try:
        client = _get_client()

        if isinstance(audio_source, bytes):
            suffix = _suffix_for_bytes(audio_source)
            # On Windows, NamedTemporaryFile can cause "Permission denied" when reopening.
            # Use an in-memory file object instead.
            f = io.BytesIO(audio_source)
            f.name = f"audio{suffix}"  # OpenAI uses filename to infer format
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
            )
        else:
            with open(audio_source, "rb") as f:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f,
                )

        # SDK returns an object with `.text` (string).
        text = getattr(result, "text", None) or ""
        text = text.strip()
        if text:
            return text, None
        return None, "Whisper returned empty text (silence or unsupported audio)."
    except Exception as e:
        return None, str(e)



 



