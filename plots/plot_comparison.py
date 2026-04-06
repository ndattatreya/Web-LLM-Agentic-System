import json
import os
import matplotlib.pyplot as plt

# -------------------------------
# CONFIG
# -------------------------------
RESULTS_PATH = "data/results/model_comparison.json"
OUTPUT_DIR = "plots"


# -------------------------------
# LOAD RESULTS
# -------------------------------
if not os.path.exists(RESULTS_PATH):
    raise FileNotFoundError(
        f"Comparison file not found: {RESULTS_PATH}\n"
        "Run `python run_full.py` first."
    )

with open(RESULTS_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

model_a_times = []
model_b_times = []

for r in results:
    model_a_times.append(r["model_a"]["inference_time_sec"])
    model_b_times.append(r["model_b"]["inference_time_sec"])


# -------------------------------
# AVERAGES
# -------------------------------
avg_a = sum(model_a_times) / len(model_a_times)
avg_b = sum(model_b_times) / len(model_b_times)


# -------------------------------
# PLOT
# -------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)

labels = ["Model A (DistilBERT)", "Model B (BERT)"]
values = [avg_a, avg_b]

plt.figure(figsize=(6, 4))
plt.bar(labels, values)
plt.ylabel("Average Inference Time (seconds)")
plt.title("Model Inference Time Comparison")

# value labels
for i, v in enumerate(values):
    plt.text(i, v, f"{v:.3f}s", ha="center", va="bottom")

output_path = os.path.join(OUTPUT_DIR, "model_comparison.png")
plt.tight_layout()
plt.savefig(output_path)
plt.show()

print(f"Plot saved to: {output_path}")
