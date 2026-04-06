import json
import os
import re
import networkx as nx
import matplotlib.pyplot as plt

# -----------------------------
# Load LLM output
# -----------------------------
base_dir = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_dir, "data", "segments", "llm_output.json")

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

entities = data["structured_data"].get("entities", [])
sentences = data["structured_data"].get("key_points", [])

# -----------------------------
# Clean entities
# -----------------------------
stop_words = {
    "The", "This", "That", "These", "Those",
    "November", "January", "React", "What"
}

cleaned_entities = []
for entity in entities:
    entity = entity.strip()

    if len(entity) < 2:
        continue

    if entity in stop_words:
        continue

    if entity not in cleaned_entities:
        cleaned_entities.append(entity)

entities = cleaned_entities

# -----------------------------
# Relation Detection
# -----------------------------
relation_patterns = {
    "uses": [
        r"\buses\b", r"\busing\b", r"\butilizes\b"
    ],
    "depends_on": [
        r"\bdepends on\b", r"\brequires\b", r"\bneeds\b"
    ],
    "contains": [
        r"\bcontains\b", r"\bincludes\b", r"\bconsists of\b"
    ],
    "supports": [
        r"\bsupports\b", r"\bpromotes\b", r"\benables\b"
    ],
    "inherits_from": [
        r"\binherits from\b", r"\bextends\b"
    ],
    "related_to": [
        r".*"
    ]
}

def detect_relation(sentence):
    sentence = sentence.lower()

    for relation, patterns in relation_patterns.items():
        for pattern in patterns:
            if re.search(pattern, sentence):
                return relation

    return "related_to"

# -----------------------------
# Node Type Detection
# -----------------------------
def get_node_type(entity):
    entity_lower = entity.lower()

    if entity_lower in ["react", "reactjs", "angular", "vue", "javascript"]:
        return "technology"

    if entity_lower in ["jsx", "hooks", "components", "dom"]:
        return "concept"

    if "class" in entity_lower:
        return "class"

    if "function" in entity_lower:
        return "function"

    return "general"

# -----------------------------
# Build Graph
# -----------------------------
G = nx.DiGraph()

for entity in entities:
    node_type = get_node_type(entity)
    G.add_node(entity, node_type=node_type)

for sentence in sentences:
    found_entities = []

    for entity in entities:
        if entity.lower() in sentence.lower():
            found_entities.append(entity)

    if len(found_entities) < 2:
        continue

    relation = detect_relation(sentence)

    for i in range(len(found_entities)):
        for j in range(i + 1, len(found_entities)):
            e1 = found_entities[i]
            e2 = found_entities[j]

            if G.has_edge(e1, e2):
                G[e1][e2]["weight"] += 1
            else:
                G.add_edge(e1, e2, relation=relation, weight=1)

# -----------------------------
# Node Colors
# -----------------------------
color_map = {
    "technology": "#4F81BD",
    "concept": "#6EC6FF",
    "class": "#F4B183",
    "function": "#A9D18E",
    "general": "#D9D9D9"
}

node_colors = [
    color_map[G.nodes[node]["node_type"]]
    for node in G.nodes()
]

# -----------------------------
# Draw Better Graph
# -----------------------------
plt.figure(figsize=(14, 10))

pos = nx.spring_layout(G, k=2.0, seed=42)

# nodes
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=3500,
    node_color=node_colors,
    edgecolors="black",
    linewidths=1.5
)

# labels
nx.draw_networkx_labels(
    G,
    pos,
    font_size=10,
    font_weight="bold"
)

# edges with thickness by weight
weights = [G[u][v]["weight"] for u, v in G.edges()]
edge_widths = [1 + w for w in weights]

nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    arrowstyle="->",
    arrowsize=20,
    width=edge_widths,
    edge_color="gray",
    connectionstyle="arc3,rad=0.08"
)

# edge labels
edge_labels = {
    (u, v): G[u][v]["relation"]
    for u, v in G.edges()
}

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    font_size=8,
    rotate=True
)

# legend
from matplotlib.patches import Patch

legend_elements = [
    Patch(facecolor=color, edgecolor="black", label=label.title())
    for label, color in color_map.items()
]

plt.legend(
    handles=legend_elements,
    loc="upper left",
    bbox_to_anchor=(1, 1)
)

plt.title("Enhanced Knowledge Graph", fontsize=16, fontweight="bold")
plt.axis("off")
plt.tight_layout()

output_path = os.path.join(base_dir, "agent", "knowledge_graph.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Knowledge graph saved to: {output_path}")

plt.show()