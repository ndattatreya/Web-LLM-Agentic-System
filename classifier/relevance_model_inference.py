import os
import torch
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
)

# Get absolute path to:
# Web-LLM-Agentic-System/relevance_model/checkpoint-14
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "relevance_model", "checkpoint-14")
)

# Optional: check whether the model folder exists
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model checkpoint folder not found:\n{MODEL_PATH}"
    )

# Optional: check whether important files exist
required_files = [
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
    "model.safetensors",
]

missing_files = [
    file_name
    for file_name in required_files
    if not os.path.exists(os.path.join(MODEL_PATH, file_name))
]

if missing_files:
    raise FileNotFoundError(
        "Missing required model files in checkpoint folder:\n"
        + "\n".join(missing_files)
    )

# Load tokenizer and model from local folder
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

# Set model to evaluation mode
model.eval()


def is_relevant_ml(text: str, threshold: float = 0.5):
    """
    Returns:
        (is_relevant, score)

    Example:
        is_relevant_ml("What is the weather today?")
        -> (True, 0.8732)
    """

    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="pt",
    )

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.softmax(outputs.logits, dim=1)

    relevance_score = probabilities[0][1].item()

    return relevance_score >= threshold, round(relevance_score, 4)


# Test block
if __name__ == "__main__":
    test_queries = [
        "What is the weather in Vijayawada today?",
        "Tell me a joke",
        "Best React interview questions",
    ]

    for query in test_queries:
        result, score = is_relevant_ml(query)

        print(f"Query: {query}")
        print(f"Relevant: {result}")
        print(f"Score: {score}")
        print("-" * 50)