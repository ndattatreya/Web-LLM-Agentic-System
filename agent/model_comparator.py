import json
import os
import time
from transformers import pipeline


# -------------------------------
# CONFIG
# -------------------------------
RESULTS_DIR = "data/results"

MODEL_A_NAME = "distilbert-base-uncased"
MODEL_B_NAME = "bert-base-uncased"

MAX_TOKENS = 512   # 🔑 critical fix


# -------------------------------
# LOAD MODELS (with truncation)
# -------------------------------
def load_models():
    model_a = pipeline(
        "feature-extraction",
        model=MODEL_A_NAME,
        tokenizer=MODEL_A_NAME,
        device=-1
    )

    model_b = pipeline(
        "feature-extraction",
        model=MODEL_B_NAME,
        tokenizer=MODEL_B_NAME,
        device=-1
    )

    return model_a, model_b


# -------------------------------
# SAFE INFERENCE (truncate)
# -------------------------------
def run_model(model, text):
    return model(
        text,
        truncation=True,
        max_length=MAX_TOKENS
    )


# -------------------------------
# COMPARE MODELS
# -------------------------------
def compare_models(relevant_segments):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    model_a, model_b = load_models()

    results = []

    for seg in relevant_segments:
        text = seg["text"]

        # ---- Model A ----
        start_a = time.time()
        _ = run_model(model_a, text)
        time_a = time.time() - start_a

        # ---- Model B ----
        start_b = time.time()
        _ = run_model(model_b, text)
        time_b = time.time() - start_b

        results.append({
            "segment_id": seg["segment_id"],
            "model_a": {
                "name": MODEL_A_NAME,
                "inference_time_sec": round(time_a, 4)
            },
            "model_b": {
                "name": MODEL_B_NAME,
                "inference_time_sec": round(time_b, 4)
            }
        })

    output_path = os.path.join(RESULTS_DIR, "model_comparison.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Model comparison saved to: {output_path}")
