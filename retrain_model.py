import json
import numpy as np
import torch
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
import warnings
warnings.filterwarnings('ignore')

# Paths
DATASET_PATH = "data/dataset.json"
MODEL_NAME = "distilbert-base-uncased"
OUTPUT_DIR = "relevance_model/checkpoint-14-retrained"

# Load dataset
print("Loading dataset...")
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [d["label"] for d in data]

print(f"Total samples: {len(texts)}")
print(f"Class distribution: 0={labels.count(0)}, 1={labels.count(1)}")

# Split: 70% train, 15% validation, 15% test
train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    texts, labels, test_size=0.3, random_state=42, stratify=labels
)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=42, stratify=temp_labels
)

print(f"Train: {len(train_texts)}, Val: {len(val_texts)}, Test: {len(test_texts)}")

# Tokenize
print("Tokenizing dataset...")
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize_function(texts, labels):
    return tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors=None
    ), labels

train_encodings = tokenizer(
    train_texts, truncation=True, padding=True, max_length=256
)
val_encodings = tokenizer(
    val_texts, truncation=True, padding=True, max_length=256
)
test_encodings = tokenizer(
    test_texts, truncation=True, padding=True, max_length=256
)

# Create datasets
train_dataset = Dataset.from_dict({
    'input_ids': train_encodings['input_ids'],
    'attention_mask': train_encodings['attention_mask'],
    'labels': train_labels
})

val_dataset = Dataset.from_dict({
    'input_ids': val_encodings['input_ids'],
    'attention_mask': val_encodings['attention_mask'],
    'labels': val_labels
})

test_dataset = Dataset.from_dict({
    'input_ids': test_encodings['input_ids'],
    'attention_mask': test_encodings['attention_mask'],
    'labels': test_labels
})

# Calculate class weights for imbalanced data
class_counts = np.bincount(train_labels)
class_weights = len(train_labels) / (len(class_counts) * class_counts)
print(f"Class weights: {class_weights}")

# Load model
print("Loading model...")
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2
)

# Training arguments with aggressive hyperparameters for better learning
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    overwrite_output_dir=True,
    num_train_epochs=10,  # More epochs
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=3e-5,  # Slightly higher LR
    weight_decay=0.01,
    warmup_steps=500,  # Gradual warmup
    logging_steps=50,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    greater_is_better=True,
    save_total_limit=3,
    seed=42,
    fp16=torch.cuda.is_available(),  # Mixed precision if GPU available
)

# Custom trainer with class weights
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        
        # Apply class weights
        loss_fn = torch.nn.CrossEntropyLoss(
            weight=torch.tensor(class_weights, dtype=torch.float64).to(model.device)
        )
        loss = loss_fn(logits, labels)
        
        return (loss, outputs) if return_outputs else loss

# Training
print("Training model...")
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=DataCollatorWithPadding(tokenizer),
    tokenizer=tokenizer,
)

trainer.train()

# Evaluation
print("\n" + "="*60)
print("TEST SET EVALUATION")
print("="*60)

predictions = trainer.predict(test_dataset)
pred_labels = np.argmax(predictions.predictions, axis=1)

accuracy = accuracy_score(test_labels, pred_labels)
precision = precision_score(test_labels, pred_labels)
recall = recall_score(test_labels, pred_labels)
f1 = f1_score(test_labels, pred_labels)

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print("\nClassification Report:")
print(classification_report(test_labels, pred_labels, target_names=['Not Relevant', 'Relevant']))

# Save model
print("\nSaving model...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Model saved to {OUTPUT_DIR}")

# Use new model for future evaluations
print("\nTo use the retrained model, update eval.py:")
print(f'MODEL_PATH = "{OUTPUT_DIR}"')
