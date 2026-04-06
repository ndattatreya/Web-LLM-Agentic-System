import os

from crawler.html_fetcher import fetch_html
from crawler.pdf_fetcher import fetch_pdf
from crawler.audio_transcriber import transcribe_audio


def load_document(source: str) -> dict:
    # ---------------- HTML URL ----------------
    if source.startswith("http"):
        result = fetch_html(source)

        return {
            "source_type": "html",
            "source_id": source,
            "text": result.get("html", ""),
            "error": result.get("error")
        }

    # ---------------- PDF ----------------
    if source.lower().endswith(".pdf"):
        return fetch_pdf(source)

    # ---------------- Audio ----------------
    if source.lower().endswith((".wav", ".mp3", ".m4a")):
        return {
            "source_type": "audio",
            "source_id": source,
            "text": transcribe_audio(source)
        }

    return {
        "error": "Unsupported input type",
        "text": ""
    }
