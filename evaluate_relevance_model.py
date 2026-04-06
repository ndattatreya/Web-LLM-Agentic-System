import json
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

MODEL_PATH = "relevance_model"
DATASET_PATH = "data/dataset.json"

# Load model & tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Load dataset
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
true_labels = [d["label"] for d in data]

predicted_labels = []

for text in texts:
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model(**inputs)
        prediction = torch.argmax(outputs.logits, dim=1).item()

    predicted_labels.append(prediction)

# Metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
f1 = f1_score(true_labels, predicted_labels)

print("Relevance Model Evaluation Results")
print("-----------------------------------")
print(f"Accuracy  : {accuracy:.4f}")
print(f"Precision : {precision:.4f}")
print(f"Recall    : {recall:.4f}")
print(f"F1-score  : {f1:.4f}")
