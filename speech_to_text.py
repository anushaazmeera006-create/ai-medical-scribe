# import os
# import tempfile
# from typing import Optional, Tuple, Union

# try:
#     from faster_whisper import WhisperModel  # type: ignore[import-not-found]
# except Exception:
#     WhisperModel = None  # type: ignore[assignment]


# def _get_model() -> "WhisperModel":
#     """
#     Load a local Whisper model once and reuse it.

#     Uses the `FAST_WHISPER_MODEL_SIZE` env var if set, otherwise "small".
#     """
#     if WhisperModel is None:
#         raise RuntimeError(
#             "faster-whisper is not installed. Run "
#             "`python -m pip install faster-whisper` first."
#         )

#     if "_whisper_model_cache" not in globals():
#         size = os.environ.get("FAST_WHISPER_MODEL_SIZE", "small")
#         globals()["_whisper_model_cache"] = WhisperModel(
#             size,
#             device="cpu",
#             compute_type="int8",
#         )
#     return globals()["_whisper_model_cache"]


# def _transcribe_path(path: str) -> Tuple[Optional[str], Optional[str]]:
#     """
#     Transcribe an audio file at `path` using faster-whisper in
#     translate-to-English mode (multilingual → English text).
#     """
#     model = _get_model()
#     try:
#         segments, _info = model.transcribe(
#             path,
#             task="translate",  # always output English text
#             language=None,  # let Whisper auto-detect language(s)
#             beam_size=5,
#         )
#         pieces = [seg.text.strip() for seg in segments if seg.text]
#         text = " ".join(pieces).strip()
#         if text:
#             return text, None
#         return None, "Whisper returned empty text (silence or unclear audio)."
#     except Exception as e:
#         return None, str(e)


# def transcribe_audio(audio_source: Union[bytes, str]) -> Tuple[Optional[str], Optional[str]]:
#     """
#     Transcribe audio into **English text** using local faster-whisper.

#     Returns
#     -------
#     (transcript, error_message). On success: (text, None). On failure: (None, error_str).
#     """
#     try:
#         if isinstance(audio_source, bytes):
#             # Write bytes to a temporary file (works reliably on Windows).
#             fd, path = tempfile.mkstemp(suffix=".wav")
#             try:
#                 with os.fdopen(fd, "wb") as tmp:
#                     tmp.write(audio_source)
#                 return _transcribe_path(path)
#             finally:
#                 try:
#                     os.remove(path)
#                 except OSError:
#                     pass
#         else:
#             # audio_source is a file path
#             return _transcribe_path(audio_source)
#     except Exception as e:
#         return None, str(e)
import os
import tempfile
from typing import Optional, Tuple, Union

try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None


def _get_model() -> "WhisperModel":
    """
    Load Faster-Whisper model once and reuse it.
    """
    if WhisperModel is None:
        raise RuntimeError(
            "faster-whisper is not installed. Run: pip install faster-whisper"
        )

    if "_whisper_model_cache" not in globals():
        size = os.environ.get("FAST_WHISPER_MODEL_SIZE", "small")

        globals()["_whisper_model_cache"] = WhisperModel(
            size,
            device="cpu",
            compute_type="int8",
        )

    return globals()["_whisper_model_cache"]


def _transcribe_path(path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio file using Faster-Whisper
    """
    model = _get_model()

    try:
        segments, _ = model.transcribe(
            path,
            task="translate",
            language=None,
            beam_size=5,
        )

        pieces = [seg.text.strip() for seg in segments if seg.text]
        text = " ".join(pieces).strip()

        if text:
            return text, None

        return None, "Whisper returned empty text."

    except Exception as e:
        return None, str(e)


def transcribe_audio(
    audio_source: Union[bytes, str],
    vosk_model_path: Optional[str] = None,   # <-- added only for compatibility
) -> Tuple[Optional[str], Optional[str]]:
    """
    Transcribe audio using Faster-Whisper.

    vosk_model_path parameter is ignored but kept so that
    it matches the function call in app.py.
    """

    try:
        if isinstance(audio_source, bytes):

            fd, path = tempfile.mkstemp(suffix=".wav")

            try:
                with os.fdopen(fd, "wb") as tmp:
                    tmp.write(audio_source)

                return _transcribe_path(path)

            finally:
                try:
                    os.remove(path)
                except OSError:
                    pass

        else:
            return _transcribe_path(audio_source)

    except Exception as e:
        return None, str(e)
