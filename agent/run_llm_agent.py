import json
import re
from collections import Counter
from pathlib import Path
from transformers import pipeline

INPUT_PATH = "../data/segments/relevant_segments.json"
OUTPUT_PATH = "../data/segments/llm_output.json"

MAX_SEGMENTS = 5
MAX_CHARS_PER_SEGMENT = 250

# --------------------------------
# Better Local LLM
# --------------------------------
llm = pipeline(
    "text2text-generation",
    model="google/flan-t5-base",
    tokenizer="google/flan-t5-base"
)

# --------------------------------
# Utilities
# --------------------------------
def truncate(text, max_chars):
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def sentence_split(text):
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if len(s.strip()) > 0
    ]


def extract_title(text):
    sentences = sentence_split(text)
    if not sentences:
        return "Untitled"

    first = sentences[0]

    if len(first) > 100:
        first = first[:100] + "..."

    return first


def extract_key_points(text, max_points=10):
    sentences = sentence_split(text)

    filtered = []
    seen = set()

    for sentence in sentences:
        words = sentence.split()

        if len(words) < 6 or len(words) > 35:
            continue

        cleaned = sentence.strip()

        if cleaned not in seen:
            filtered.append(cleaned)
            seen.add(cleaned)

    return filtered[:max_points]


def extract_entities(text, top_k=15):
    # Better entity extraction using grouped capitalized phrases
    matches = re.findall(
        r"\b(?:[A-Z][a-zA-Z0-9+\-]*)(?:\s+[A-Z][a-zA-Z0-9+\-]*)*\b",
        text
    )

    stop_words = {
        "The", "This", "That", "These", "Those",
        "Text", "Summary", "Conclusion",
        "Page", "Section", "Chapter"
    }

    cleaned = []

    for match in matches:
        match = match.strip()

        if match in stop_words:
            continue

        if len(match) < 3:
            continue

        cleaned.append(match)

    common = Counter(cleaned).most_common(top_k)
    return [entity for entity, _ in common]


def classify_relation(sentence):
    sentence = sentence.lower()

    relation_rules = {
        "uses": ["uses", "using", "utilizes"],
        "depends_on": ["depends on", "requires", "needs"],
        "contains": ["contains", "includes", "consists of"],
        "supports": ["supports", "enables", "improves"],
        "related_to": []
    }

    for relation, keywords in relation_rules.items():
        for keyword in keywords:
            if keyword in sentence:
                return relation

    return "related_to"


def build_relationships(sentences, entities):
    relationships = []

    for sentence in sentences:
        found = []

        for entity in entities:
            if entity.lower() in sentence.lower():
                found.append(entity)

        if len(found) < 2:
            continue

        relation = classify_relation(sentence)

        for i in range(len(found)):
            for j in range(i + 1, len(found)):
                relationships.append({
                    "source": found[i],
                    "target": found[j],
                    "relation": relation,
                    "sentence": sentence
                })

    return relationships


# --------------------------------
# Main
# --------------------------------
def main():
    input_file = Path(INPUT_PATH)
    output_file = Path(OUTPUT_PATH)

    with open(input_file, "r", encoding="utf-8") as f:
        segments = json.load(f)

    # Keep only best segments
    segments = segments[:MAX_SEGMENTS]

    cleaned_segments = []

    for seg in segments:
        text = truncate(seg.get("text", ""), MAX_CHARS_PER_SEGMENT)

        if len(text) > 40:
            cleaned_segments.append(text)

    combined_text = "\n".join(cleaned_segments[:5])

    prompt = f"""
Summarize the following content in a clean and factual way.

Return:
1. A short title
2. Important points
3. Main technologies, concepts, or entities mentioned

Content:
{combined_text}
"""

    print("Running improved LLM pipeline...")

    result = llm(
        prompt,
        max_new_tokens=300,
        do_sample=False
    )

    llm_output = result[0]["generated_text"].strip()

    title = extract_title(llm_output)
    key_points = extract_key_points(llm_output)
    entities = extract_entities(llm_output)
    relationships = build_relationships(key_points, entities)

    output = {
        "segments_used": len(cleaned_segments),
        "summary": llm_output,
        "structured_data": {
            "title": title,
            "key_points": key_points,
            "entities": entities,
            "relationships": relationships
        }
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\nProcessing complete.")
    print(f"Segments used: {len(cleaned_segments)}")
    print(f"Entities found: {len(entities)}")
    print(f"Relationships found: {len(relationships)}")
    print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()