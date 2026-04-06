import json
import os
import sys
import tkinter as tk
from tkinter import filedialog

from crawler.document_loader import load_document
from agent.content_extractor import extract_main_content
from agent.pdf_cleaner import clean_pdf_text
from classifier.relevance_model_inference import is_relevant_ml
from agent.model_comparator import compare_models
import warnings

# Silence HuggingFace + Transformers logs
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"

warnings.filterwarnings("ignore")

from transformers import logging
logging.set_verbosity_error()

# -------------------------------
# CONFIG
# -------------------------------
MAX_WORDS_PER_SEGMENT = 50      # smaller → more segments
MAX_RELEVANT_SEGMENTS = 20
SEGMENTS_DIR = "data/segments"


# -------------------------------
# File picker
# -------------------------------
def pick_file():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_path = filedialog.askopenfilename(
        title="Select PDF / Audio file",
        filetypes=[
            ("Supported files", "*.pdf *.mp3 *.wav *.m4a"),
            ("All files", "*.*")
        ]
    )

    root.destroy()
    return file_path


# -------------------------------
# Segmentation
# -------------------------------
def split_text(text, max_words=MAX_WORDS_PER_SEGMENT):
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


# -------------------------------
# MAIN PIPELINE
# -------------------------------
def main():

    # 1️⃣ Input
    if len(sys.argv) > 1:
        input_source = sys.argv[1]
    else:
        print("Select a file (PDF / Audio). Cancel to enter URL.")
        input_source = pick_file() or input("Enter URL: ").strip()

    if not input_source:
        print("No input provided.")
        return

    # 2️⃣ Load document
    print("Loading document...")
    doc = load_document(input_source)

    raw_text = doc.get("text", "")
    source_type = doc.get("source_type", "")
    source_id = doc.get("source_id", "")

    # HTML sometimes returns dict
    if isinstance(raw_text, dict):
        text = raw_text.get("html", "")
    else:
        text = raw_text

    if not isinstance(text, str) or not text.strip():
        print("Extraction stopped: No text extracted.")
        print("Reason:", doc.get("error", "Unknown"))
        return

    # 3️⃣ Cleaning
    print("Preparing main content...")

    if source_type == "pdf":
        clean_text = clean_pdf_text(text)
    elif source_type == "html":
        raw = extract_main_content(text)
        clean_text = extract_main_content(raw)

    else:  # audio
        clean_text = text

    if not clean_text.strip():
        print("No meaningful content extracted.")
        return

    # 4️⃣ Segmentation
    segments_raw = split_text(clean_text)

    os.makedirs(SEGMENTS_DIR, exist_ok=True)

    segments = [
        {"segment_id": f"seg_{i}", "text": seg}
        for i, seg in enumerate(segments_raw)
    ]

    with open(f"{SEGMENTS_DIR}/segments.json", "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2, ensure_ascii=False)

    print(f"Total segments extracted: {len(segments)}")

    # 5️⃣ Relevance filtering
    print("Running relevance filter...")
    relevant_segments = []

    # 🔥 IMPORTANT FIX
    if source_type == "audio":
        print("Audio detected → skipping relevance model")
        relevant_segments = segments[:MAX_RELEVANT_SEGMENTS]

        # add metadata
        for seg in relevant_segments:
            seg["relevance_score"] = 1.0
            seg["source_id"] = source_id
            seg["source_type"] = source_type

    else:
        for seg in segments:
            if len(relevant_segments) >= MAX_RELEVANT_SEGMENTS:
                break
            try:
                keep, score = is_relevant_ml(seg["text"])

                if keep:
                    relevant_segments.append({
                        "segment_id": seg["segment_id"],
                        "text": seg["text"],
                        "relevance_score": round(score, 4),
                        "source_id": source_id,
                        "source_type": source_type
                    })
            except Exception as e:
                print(f"[WARN] Relevance failed for {seg['segment_id']}: {e}")

    with open(f"{SEGMENTS_DIR}/relevant_segments.json", "w", encoding="utf-8") as f:
        json.dump(relevant_segments, f, indent=2, ensure_ascii=False)

    print(f"Relevant segments kept: {len(relevant_segments)}")

    # 6️⃣ Model comparison
    if relevant_segments:
        print("Running model comparison (DistilBERT vs BERT)...")
        compare_models(relevant_segments)
        print("Model comparison completed.")
        print("Next step: python plots/plot_comparison.py")
    else:
        print("No relevant segments found. Skipping model comparison.")


# -------------------------------
# ENTRY POINT
# -------------------------------
if __name__ == "__main__":
    main()
