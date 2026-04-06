import os
from faster_whisper import WhisperModel

_MODEL = None


def _load_model():
    global _MODEL
    if _MODEL is None:
        print("Loading Faster-Whisper model (tiny, CPU)...")
        _MODEL = WhisperModel(
            "tiny",            # ✅ positional argument (IMPORTANT)
            device="cpu",
            compute_type="int8"
        )
    return _MODEL


def transcribe_audio(file_path: str) -> str:
    if not os.path.exists(file_path):
        return ""

    model = _load_model()

    segments, _ = model.transcribe(
        file_path,
        beam_size=1,
        vad_filter=True
    )

    texts = [seg.text.strip() for seg in segments if seg.text.strip()]
    return " ".join(texts)
