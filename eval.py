import json
import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

MODEL_PATH = "relevance_model/checkpoint-14"
TOKENIZER_PATH = "relevance_model"
DATASET_PATH = "data/dataset.json"

# Load model & tokenizer
tokenizer = DistilBertTokenizerFast.from_pretrained(TOKENIZER_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Load dataset
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
true_labels = [d["label"] for d in data]

# Get confidence scores instead of raw predictions
confidences = []

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
        probs = torch.softmax(outputs.logits, dim=1)[0]
    
    confidences.append(probs.cpu().numpy())

confidences = np.array(confidences)

# Analyze dataset
class_counts = np.bincount(true_labels)
print("Dataset Analysis")
print(f"Total samples: {len(true_labels)}")
print(f"Class 0 (not relevant): {class_counts[0]} ({class_counts[0]/len(true_labels)*100:.1f}%)")
print(f"Class 1 (relevant): {class_counts[1]} ({class_counts[1]/len(true_labels)*100:.1f}%)")
print()

# Test different thresholds
print("Threshold Optimization")
best_accuracy = 0
best_threshold = 0.5
best_metrics = {}

for threshold in np.arange(0.1, 0.9, 0.05):
    predicted = (confidences[:, 1] >= threshold).astype(int)
    acc = accuracy_score(true_labels, predicted)
    
    if acc > best_accuracy:
        best_accuracy = acc
        best_threshold = threshold
        best_metrics = {
            'accuracy': acc,
            'precision': precision_score(true_labels, predicted, zero_division=0),
            'recall': recall_score(true_labels, predicted, zero_division=0),
            'f1': f1_score(true_labels, predicted, zero_division=0)
        }
    
    print(f"Threshold {threshold:.2f}: Acc={acc:.4f}, Prec={precision_score(true_labels, predicted, zero_division=0):.4f}, Rec={recall_score(true_labels, predicted, zero_division=0):.4f}")

print()
print("Default Threshold (0.5)")
predicted_default = (confidences[:, 1] >= 0.5).astype(int)
print(f"Accuracy  : {accuracy_score(true_labels, predicted_default):.4f}")
print(f"Precision : {precision_score(true_labels, predicted_default):.4f}")
print(f"Recall    : {recall_score(true_labels, predicted_default):.4f}")
print(f"F1-score  : {f1_score(true_labels, predicted_default):.4f}")
cm = confusion_matrix(true_labels, predicted_default)
print(f"Confusion Matrix:\n{cm}")

print()
print("Optimized Threshold ({:.2f})".format(best_threshold))
predicted_optimized = (confidences[:, 1] >= best_threshold).astype(int)
print(f"Accuracy  : {best_metrics['accuracy']:.4f}")
print(f"Precision : {best_metrics['precision']:.4f}")
print(f"Recall    : {best_metrics['recall']:.4f}")
print(f"F1-score  : {best_metrics['f1']:.4f}")
cm_opt = confusion_matrix(true_labels, predicted_optimized)
print(f"Confusion Matrix:\n{cm_opt}")

print()
print("Recommendation")
improvement = (best_metrics['accuracy'] - accuracy_score(true_labels, predicted_default)) * 100
print(f"Using threshold {best_threshold:.2f} improves accuracy by {improvement:+.2f}%")
print(f"New accuracy: {best_metrics['accuracy']:.4f}")
