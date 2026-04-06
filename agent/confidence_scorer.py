import os
import json
import re
from collections import Counter

# ---------------------------------
# Absolute Paths
# ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "data", "segments", "llm_output.json")
)

OUTPUT_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "data", "segments", "llm_output_with_confidence.json")
)

# ---------------------------------
# Helpers
# ---------------------------------
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    return " ".join(text.split())


def keyword_overlap(point, entities):
    point_words = set(normalize(point).split())
    entity_words = set()

    for entity in entities:
        entity_words.update(normalize(entity).split())

    if not point_words:
        return 0.0

    overlap = len(point_words & entity_words)
    return overlap / len(point_words)


def source_strength(index, total_points):
    return 1 - (index / max(total_points, 1))


# ---------------------------------
# Main Function
# ---------------------------------
def score_relevance():
    # Check input exists
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_PATH}"
        )

    # Load input JSON
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    structured = data.get("structured_data", {})
    key_points = structured.get("key_points", [])
    entities = structured.get("entities", [])
    relationships = structured.get("relationships", [])

    # Count entity importance from relationships
    entity_counter = Counter()

    for relation in relationships:
        source = relation.get("source", "")
        target = relation.get("target", "")

        if source:
            entity_counter[source] += 1

        if target:
            entity_counter[target] += 1

    max_entity_freq = max(entity_counter.values()) if entity_counter else 1

    scored_points = []

    # Score every key point
    for idx, point in enumerate(key_points):
        normalized_point = normalize(point)

        # 1. Entity overlap score
        overlap_score = keyword_overlap(point, entities)

        # 2. Relationship support score
        relation_hits = 0

        for rel in relationships:
            sentence = rel.get("sentence", "")
            if normalize(sentence) == normalized_point:
                relation_hits += 1

        relationship_score = min(relation_hits / 3, 1.0)

        # 3. Position score
        position_score = source_strength(idx, len(key_points))

        # 4. Entity importance score
        entity_score = 0.0

        for entity in entities:
            if entity.lower() in point.lower():
                entity_score += (
                    entity_counter.get(entity, 0) / max_entity_freq
                )

        entity_score = min(entity_score / 3, 1.0)

        # Final weighted score
        confidence = (
            0.35 * overlap_score
            + 0.30 * relationship_score
            + 0.20 * position_score
            + 0.15 * entity_score
        )

        confidence = round(confidence, 2)

        # Confidence label
        if confidence >= 0.75:
            level = "High"
        elif confidence >= 0.45:
            level = "Medium"
        else:
            level = "Low"

        # Why explanation
        why = []

        if overlap_score > 0.3:
            why.append("contains important entities")

        if relationship_score > 0:
            why.append("supported by multiple relationships")

        if position_score > 0.7:
            why.append("appears early in summary")

        if entity_score > 0.4:
            why.append("mentions important entities")

        scored_points.append({
            "text": point,
            "confidence": confidence,
            "level": level,
            "why": why
        })

    # Final output structure
    output = {
        "title": structured.get("title", ""),
        "summary": data.get("summary", ""),
        "entities": entities,
        "relationships": relationships,
        "key_points_with_confidence": scored_points
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Save result
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Improved confidence scoring complete.")
    print("Input :", INPUT_PATH)
    print("Output:", OUTPUT_PATH)

    return output


# ---------------------------------
# Run Directly
# ---------------------------------
if __name__ == "__main__":
    score_relevance()