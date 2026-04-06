import json

with open("data/segments/segments.json", "r", encoding="utf-8") as f:
    all_segments = json.load(f)

with open("data/segments/relevant_segments.json", "r", encoding="utf-8") as f:
    relevant_segments = json.load(f)

relevant_ids = {s["segment_id"] for s in relevant_segments}

dataset = []

for seg in all_segments:
    label = 1 if seg["segment_id"] in relevant_ids else 0
    dataset.append({
        "text": seg["text"],
        "label": label
    })

with open("data/dataset.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print("Dataset created:", len(dataset))
