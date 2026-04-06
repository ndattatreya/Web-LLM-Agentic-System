from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    Trainer,
    TrainingArguments
)
import json
import torch

# Load dataset
with open("data/dataset.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = [d["text"] for d in data]
labels = [d["label"] for d in data]

tokenizer = DistilBertTokenizerFast.from_pretrained(
    "distilbert-base-uncased"
)

encodings = tokenizer(
    texts,
    truncation=True,
    padding=True,
    max_length=256
)

class RelevanceDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

dataset = RelevanceDataset(encodings, labels)

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=2
)

training_args = TrainingArguments(
    output_dir="relevance_model",
    num_train_epochs=7,
    per_device_train_batch_size=8,
    logging_steps=50,
    save_steps=500,
    save_total_limit=1,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

trainer.train()

trainer.save_model("relevance_model")
tokenizer.save_pretrained("relevance_model")

print("Fine-tuned relevance model saved.")
