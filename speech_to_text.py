
import io
import json
import os
import wave
from typing import Optional, Tuple, Union

try:
    from openai import OpenAI
except Exception:
    OpenAI = None  # type: ignore[assignment]


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


def _get_client() -> "OpenAI":
    # Module-level cache avoids re-creating the client on each call.
    if "_openai_client_cache" not in globals():
        if OpenAI is None:
            raise RuntimeError("openai package is not installed.")
        globals()["_openai_client_cache"] = OpenAI()
    return globals()["_openai_client_cache"]


def _transcribe_wav_vosk(audio_bytes: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Free/offline fallback using Vosk (WAV PCM recommended).

    Requirements:
    - pip install vosk
    - Download a Vosk model and set VOSK_MODEL_PATH to the folder path
    """
    try:
        from vosk import KaldiRecognizer, Model  # type: ignore[import-not-found]
    except Exception:
        return (
            None,
            "Offline STT is not installed. Run: `python -m pip install vosk` "
            "and download a Vosk model, then set VOSK_MODEL_PATH.",
        )

    model_path = os.environ.get("VOSK_MODEL_PATH", "").strip()
    if not model_path:
        return (
            None,
            "Offline STT needs a Vosk model. Download a model and set "
            "`VOSK_MODEL_PATH` to that folder.",
        )

    try:
        wf = wave.open(io.BytesIO(audio_bytes), "rb")
    except Exception:
        return None, "Offline STT (Vosk) only supports WAV audio bytes."

    with wf:
        # Vosk works best with 16k mono PCM, but can still run with other rates.
        recognizer = KaldiRecognizer(Model(model_path), wf.getframerate())
        recognizer.SetWords(True)

        parts: list[str] = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                try:
                    res = json.loads(recognizer.Result())
                    txt = (res.get("text") or "").strip()
                    if txt:
                        parts.append(txt)
                except Exception:
                    pass
        try:
            final = json.loads(recognizer.FinalResult())
            final_txt = (final.get("text") or "").strip()
        except Exception:
            final_txt = ""

    full = " ".join([*parts, final_txt]).strip()
    if not full:
        return None, "Offline STT returned empty text (silence or unclear audio)."
    return full, None


def transcribe_audio(audio_source: Union[bytes, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio into text using OpenAI Whisper API.

    Returns
    -------
    (transcript, error_message). On success: (text, None). On failure: (None, error_str).
    """
    # If no API key (or user doesn't want to pay), use offline fallback automatically.
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if isinstance(audio_source, bytes) and (not api_key):
        return _transcribe_wav_vosk(audio_source)

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
        # If API fails (quota/invalid key), try offline fallback for WAV bytes.
        if isinstance(audio_source, bytes) and audio_source.startswith(b"RIFF"):
            txt, err = _transcribe_wav_vosk(audio_source)
            if txt:
                return txt, None
            # Prefer original error if offline isn't available.
            return None, f"{e} (offline fallback: {err})"
        return None, str(e)





 




