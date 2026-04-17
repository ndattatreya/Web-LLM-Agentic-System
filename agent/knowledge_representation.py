from __future__ import annotations

from collections import Counter, defaultdict
from functools import lru_cache
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import spacy
except ImportError:  # pragma: no cover - fallback only when dependency is unavailable
    spacy = None


MAX_NODES = 12
MAX_RELATIONS = 10

RELATION_MAP = {
    "owned by": "owned_by",
    "published by": "published_by",
    "published in": "published_in",
    "founded by": "founded_by",
    "editor": "edited_by",
    "edited by": "edited_by",
    "headquarters": "headquartered_in",
    "located in": "located_in",
    "based in": "based_in",
    "sister newspaper": "related_publication",
    "acquired": "acquired_by",
    "studying in": "studies_in",
    "study in": "studies_in",
    "studies in": "studies_in",
    "moving to": "moves_to",
    "move to": "moves_to",
    "protects": "protects",
    "protect": "protects",
    "threatens": "challenges",
    "threaten": "challenges",
    "uses": "uses",
    "use": "uses",
    "compared to": "compared_to",
    "causes": "causes",
    "cause": "causes",
    "affects": "affects",
    "affect": "affects",
    "works on": "works_on",
    "work on": "works_on",
}

FALLBACK_RELATION_HINTS = [
    ("published by", "published_by"),
    ("issued by", "published_by"),
    ("released by", "published_by"),
    ("located in", "located_in"),
    ("part of", "part_of"),
    ("member of", "member_of"),
    ("belongs to", "belongs_to"),
    ("includes", "includes"),
    ("include", "includes"),
    ("organized by", "organized_by"),
    ("celebrated on", "celebrated_on"),
    ("born on", "born_on"),
    ("works for", "works_for"),
    ("studying in", "studies_in"),
    ("moving to", "moves_to"),
    ("protects", "protects"),
    ("threatens", "challenges"),
    ("uses", "uses"),
    ("compared to", "compared_to"),
    ("causes", "causes"),
    ("affects", "affects"),
    ("mentions", "mentions"),
    ("mentioned", "mentions"),
]

NODE_TYPE_PRIORITY = {
    "Person": 7,
    "Newspaper": 7,
    "Company": 6,
    "Organization": 5,
    "Country": 5,
    "City": 5,
    "Website": 4,
    "Technology": 4,
    "Concept": 3,
}

GENERIC_STOP_WORDS = {
    "a",
    "about",
    "after",
    "again",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "before",
    "but",
    "by",
    "can",
    "could",
    "did",
    "do",
    "does",
    "during",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "he",
    "her",
    "his",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "let",
    "may",
    "me",
    "might",
    "more",
    "most",
    "much",
    "my",
    "no",
    "not",
    "of",
    "on",
    "or",
    "our",
    "page",
    "section",
    "should",
    "so",
    "such",
    "than",
    "that",
    "the",
    "their",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "under",
    "up",
    "was",
    "we",
    "were",
    "what",
    "when",
    "which",
    "who",
    "will",
    "with",
    "would",
    "you",
    "your",
    "april",
    "january",
    "february",
    "march",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
}

ENTITY_LABEL_EXCLUDE = {
    "DATE",
    "TIME",
    "ORDINAL",
    "CARDINAL",
    "PERCENT",
    "MONEY",
    "QUANTITY",
}

METADATA_ENTITY_HINTS = {
    "photo credit",
    "published",
    "updated",
    "read more",
    "follow us",
    "subscribe",
}

FALLBACK_STOPWORDS = {
    "the", "a", "an", "this", "that", "these", "those",
    "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "in", "on", "for", "with", "and", "or",
    "by", "as", "from", "at", "it", "its", "their", "they",
    "them", "his", "her", "ours", "your", "into", "than",
}

TECH_HINTS = {
    "ai",
    "api",
    "fastapi",
    "javascript",
    "json",
    "llm",
    "python",
    "react",
    "reactjs",
    "spacy",
    "web",
}

COUNTRY_HINTS = {
    "india",
    "united states",
    "united kingdom",
    "usa",
    "u.s.",
    "france",
    "germany",
    "canada",
    "australia",
    "japan",
    "china",
}

CITY_HINTS = {
    "mumbai",
    "delhi",
    "new york",
    "london",
    "paris",
    "tokyo",
    "beijing",
    "singapore",
    "sydney",
    "dubai",
}

COMPANY_HINTS = {
    "co",
    "co.",
    "company",
    "corporation",
    "corp",
    "inc",
    "llc",
    "limited",
    "ltd",
    "pvt",
}

NEWSPAPER_HINTS = {
    "times",
    "newspaper",
    "daily",
    "herald",
    "post",
    "tribune",
    "guardian",
    "news",
}

WEBSITE_HINTS = {
    ".com",
    ".org",
    ".net",
    "website",
    "www.",
    "http://",
    "https://",
}


def normalize_entity(text: str) -> str:
    return " ".join(text.strip().split()).lower()


def strip_entity_text(text: str) -> str:
    return " ".join(part for part in text.replace("\n", " ").split()).strip(" ,;:.()[]{}\"')(")


def contains_any(text: str, keywords: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def is_valid_entity_text(text: str) -> bool:
    normalized = normalize_entity(text)
    if not normalized:
        return False

    tokens = normalized.split()
    if len(tokens) > 5:
        return False

    if len(tokens) == 1 and tokens[0] in GENERIC_STOP_WORDS:
        return False

    if all(token in GENERIC_STOP_WORDS for token in tokens):
        return False

    if len(tokens) == 1 and len(tokens[0]) <= 2:
        return False

    if sum(1 for token in tokens if token not in GENERIC_STOP_WORDS) == 0:
        return False

    if is_metadata_like_entity(normalized):
        return False

    return True


def is_metadata_like_entity(normalized_text: str) -> bool:
    if not normalized_text:
        return True

    if normalized_text in METADATA_ENTITY_HINTS:
        return True

    if any(hint in normalized_text for hint in METADATA_ENTITY_HINTS):
        return True

    # Reject time-like tokens such as 09:37 pm or 10:45am.
    if re.fullmatch(r"\d{1,2}:\d{2}(?:\s?[ap]m)?", normalized_text):
        return True

    # Reject compact date-like strings.
    if re.fullmatch(r"\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?", normalized_text):
        return True

    # Reject month + year/day forms.
    if re.search(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b", normalized_text):
        return True

    # Reject weekday-only tags.
    if normalized_text in {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}:
        return True

    return False


def entity_type_for(label: str, text: str) -> str:
    normalized = normalize_entity(text)

    if label == "PERSON":
        return "Person"

    if label == "ORG":
        if contains_any(normalized, WEBSITE_HINTS):
            return "Website"
        if contains_any(normalized, NEWSPAPER_HINTS):
            return "Newspaper"
        if contains_any(normalized, COMPANY_HINTS):
            return "Company"
        return "Organization"

    if label in {"GPE", "LOC", "FAC"}:
        if normalized in COUNTRY_HINTS:
            return "Country"
        if normalized in CITY_HINTS:
            return "City"
        if normalized in {"india", "usa", "uk"}:
            return "Country"
        return "City"

    if label in {"PRODUCT", "WORK_OF_ART", "EVENT", "LAW", "LANGUAGE"}:
        return "Concept"

    if contains_any(normalized, TECH_HINTS):
        return "Technology"

    if contains_any(normalized, WEBSITE_HINTS):
        return "Website"

    if contains_any(normalized, NEWSPAPER_HINTS):
        return "Newspaper"

    return "Concept"


def canonicalize_token(token: str) -> str:
    token = token.lower().strip()
    if len(token) <= 3:
        return token
    if token.endswith("ies"):
        return token[:-3] + "y"
    if token.endswith("ves"):
        return token[:-3] + "f"
    if token.endswith("es") and not token.endswith(("ses", "xes", "zes", "ches", "shes")):
        return token[:-2]
    if token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def canonical_entity_key(text: str) -> str:
    cleaned = normalize_entity(text)
    tokens = [canonicalize_token(token) for token in cleaned.split() if token]
    return " ".join(tokens)


def display_entity_text(text: str) -> str:
    cleaned = strip_entity_text(text)
    parts = []
    for raw_part in cleaned.split():
        if raw_part.isupper() and len(raw_part) <= 5:
            parts.append(raw_part)
        else:
            parts.append(raw_part[:1].upper() + raw_part[1:].lower())
    return " ".join(parts)


def extract_noun_phrase_candidates(sentence: Any) -> List[Dict[str, Any]]:
    if sentence is None or not hasattr(sentence, "noun_chunks"):
        return []

    phrases: List[Dict[str, Any]] = []
    for chunk in sentence.noun_chunks:
        phrase_text = strip_entity_text(chunk.text)
        if not is_valid_entity_text(phrase_text):
            continue

        phrase_type = entity_type_for(getattr(chunk.root, "ent_type_", ""), phrase_text)
        if phrase_type == "Concept" and len(phrase_text.split()) == 1:
            continue

        phrases.append(
            {
                "text": phrase_text,
                "type": phrase_type,
                "start": int(chunk.start_char),
                "end": int(chunk.end_char),
            }
        )

    return phrases


def node_level_for(entity_type: str, importance: float, is_main_topic: bool = False) -> str:
    if is_main_topic:
        return "Main Topic"
    if importance >= 12.0:
        return "Subtopic"
    if entity_type in {"Person", "Organization", "Company", "Country", "City", "Technology"}:
        return "Entity"
    return "Supporting Detail"


def relation_to_display_phrase(phrase: str, relation: str) -> str:
    if phrase:
        return phrase
    return relation.replace("_", " ")


def relation_likelihood_score(relation: str) -> int:
    return relation_priority(relation)


def is_important_node(record: Dict[str, Any]) -> bool:
    return record.get("importance", 0.0) >= 10.0 or record.get("level") == "Main Topic"


def score_entity(entity: Dict[str, Any]) -> float:
    occurrence_score = min(entity["count"], 5) * 2.0
    type_score = NODE_TYPE_PRIORITY.get(entity["type"], 3)
    spread_score = min(len(entity["sentences"]), 3) * 0.75
    early_bonus = max(0.0, 2.5 - entity["first_sentence_index"] * 0.25)
    return round(occurrence_score + type_score + spread_score + early_bonus, 4)


def extract_entity_records_fallback(text: str, top_k: int = 15) -> List[Dict[str, Any]]:
    words = re.findall(r"\b[a-zA-Z][a-zA-Z\-]{2,}\b", text.lower())
    filtered = [
        word for word in words
        if word not in FALLBACK_STOPWORDS
        and word not in GENERIC_STOP_WORDS
        and len(word) > 3
    ]

    common = Counter(filtered).most_common(top_k)
    if not common:
        return []

    entity_records: List[Dict[str, Any]] = []
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    for index, (word, count) in enumerate(common):
        sentence_indexes = [
            i for i, sentence in enumerate(sentences)
            if word in sentence.lower()
        ]
        first_index = sentence_indexes[0] if sentence_indexes else index

        record = {
            "id": display_entity_text(word),
            "type": "Concept",
            "count": count,
            "sentences": sentence_indexes,
            "first_sentence_index": first_index,
            "confidence": 0.0,
            "spans": [],
            "aliases": {word},
            "importance": 0.0,
            "level": "Supporting Detail",
            "source_sentence": sentences[first_index] if sentence_indexes and first_index < len(sentences) else "",
        }
        record["confidence"] = score_entity(record)
        entity_records.append(record)

    entity_records.sort(
        key=lambda item: (
            item["confidence"],
            item["count"],
            -item["first_sentence_index"],
        ),
        reverse=True,
    )
    return entity_records


def relation_priority(relation: str) -> int:
    priority = {
        "owned_by": 7,
        "founded_by": 7,
        "studies_in": 7,
        "protects": 7,
        "published_by": 6,
        "published_in": 6,
        "headquartered_in": 6,
        "based_in": 5,
        "located_in": 5,
        "edited_by": 5,
        "moves_to": 5,
        "works_on": 5,
        "compared_to": 5,
        "causes": 5,
        "affects": 5,
        "related_publication": 4,
        "acquired_by": 4,
        "uses": 4,
        "challenges": 4,
    }
    return priority.get(relation, 3)


@lru_cache(maxsize=1)
def load_nlp():
    if spacy is None:
        return None

    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        try:
            from spacy.cli import download

            download("en_core_web_sm")
            return spacy.load("en_core_web_sm")
        except Exception:
            return None


def iter_sentences(doc: Any, texts: Sequence[str]) -> Iterable[Any]:
    if doc is not None and getattr(doc, "sents", None):
        for sentence in doc.sents:
            sentence_text = sentence.text.strip()
            if sentence_text:
                yield sentence
        return

    for text in texts:
        for sentence in text.split("."):
            sentence_text = sentence.strip()
            if sentence_text:
                yield sentence_text


def extract_entity_records(text: str) -> List[Dict[str, Any]]:
    nlp = load_nlp()
    if nlp is None:
        return extract_entity_records_fallback(text)

    doc = nlp(text)
    records: Dict[str, Dict[str, Any]] = {}

    for sentence_index, sentence in enumerate(iter_sentences(doc, [text])):
        sentence_text = sentence.text if hasattr(sentence, "text") else str(sentence)
        sentence_lower = sentence_text.lower()

        candidate_chunks = extract_noun_phrase_candidates(sentence)

        for ent in getattr(sentence, "ents", []) if hasattr(sentence, "ents") else []:
            if ent.label_ in ENTITY_LABEL_EXCLUDE:
                continue

            entity_text = strip_entity_text(ent.text)
            if not is_valid_entity_text(entity_text):
                continue

            entity_key = canonical_entity_key(entity_text)
            entity_type = entity_type_for(ent.label_, entity_text)
            record = records.setdefault(
                entity_key,
                {
                    "id": display_entity_text(entity_text),
                    "type": entity_type,
                    "count": 0,
                    "sentences": set(),
                    "first_sentence_index": sentence_index,
                    "confidence": 0.0,
                    "spans": [],
                    "aliases": set(),
                    "importance": 0.0,
                    "level": "Supporting Detail",
                    "source_sentence": sentence_text,
                },
            )

            record["aliases"].add(entity_text)
            record["id"] = record["id"] if len(record["id"]) >= len(display_entity_text(entity_text)) else display_entity_text(entity_text)
            if NODE_TYPE_PRIORITY.get(entity_type, 0) > NODE_TYPE_PRIORITY.get(record["type"], 0):
                record["type"] = entity_type

            record["count"] += 1
            record["sentences"].add(sentence_index)
            record["spans"].append(
                {
                    "start": int(ent.start_char),
                    "end": int(ent.end_char),
                    "sentence_index": sentence_index,
                    "sentence_text": sentence_text,
                }
            )

        for chunk in candidate_chunks:
            phrase_text = chunk["text"]
            entity_key = canonical_entity_key(phrase_text)
            entity_type = chunk["type"]
            record = records.setdefault(
                entity_key,
                {
                    "id": display_entity_text(phrase_text),
                    "type": entity_type,
                    "count": 0,
                    "sentences": set(),
                    "first_sentence_index": sentence_index,
                    "confidence": 0.0,
                    "spans": [],
                    "aliases": set(),
                    "importance": 0.0,
                    "level": "Supporting Detail",
                    "source_sentence": sentence_text,
                },
            )

            record["aliases"].add(phrase_text)
            if len(display_entity_text(phrase_text)) > len(record["id"]):
                record["id"] = display_entity_text(phrase_text)
            if NODE_TYPE_PRIORITY.get(entity_type, 0) > NODE_TYPE_PRIORITY.get(record["type"], 0):
                record["type"] = entity_type
            record["count"] += 1
            record["sentences"].add(sentence_index)
            record["spans"].append(
                {
                    "start": int(chunk["start"]),
                    "end": int(chunk["end"]),
                    "sentence_index": sentence_index,
                    "sentence_text": sentence_text,
                }
            )

    entity_list: List[Dict[str, Any]] = []
    for record in records.values():
        record["sentences"] = sorted(record["sentences"])
        record["confidence"] = score_entity(record)
        record["importance"] = round(record["confidence"] + min(len(record.get("aliases", [])), 5) * 0.35, 4)
        entity_list.append(record)

    entity_list.sort(
        key=lambda item: (
            item["confidence"],
            NODE_TYPE_PRIORITY.get(item["type"], 0),
            item["count"],
            -item["first_sentence_index"],
        ),
        reverse=True,
    )

    if entity_list:
        return entity_list

    return extract_entity_records_fallback(text)


def build_node_payload(entity_records: Sequence[Dict[str, Any]], max_nodes: int = MAX_NODES) -> List[Dict[str, Any]]:
    nodes = []
    sorted_records = sorted(
        entity_records,
        key=lambda item: (
            item.get("importance", 0.0),
            item.get("confidence", 0.0),
            len(item.get("sentences", [])),
            -item.get("first_sentence_index", 0),
        ),
        reverse=True,
    )

    main_topic = sorted_records[0] if sorted_records else None

    for record in sorted_records[:max_nodes]:
        nodes.append(
            {
                "id": record["id"],
                "type": record["type"],
                "confidence": round(float(record["confidence"]), 4),
                "mentions": record["count"],
                "importance": round(float(record.get("importance", record["confidence"])), 4),
                "level": node_level_for(record["type"], float(record.get("importance", record["confidence"])), record is main_topic),
                "source_sentence": record.get("source_sentence", ""),
                "aliases": sorted(str(alias) for alias in record.get("aliases", set())),
            }
        )
    return nodes


def prune_graph(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]], max_nodes: int, max_relations: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if not nodes:
        return [], []

    degree_map = Counter()
    for edge in edges:
        degree_map[normalize_entity(edge["source"])] += 1
        degree_map[normalize_entity(edge["target"])] += 1

    ranked_nodes = sorted(
        nodes,
        key=lambda node: (
            node.get("importance", node.get("confidence", 0.0)),
            node.get("confidence", 0.0),
            degree_map.get(normalize_entity(node["id"]), 0),
        ),
        reverse=True,
    )

    retained_nodes: List[Dict[str, Any]] = []
    main_topic_included = False
    for node in ranked_nodes:
        degree = degree_map.get(normalize_entity(node["id"]), 0)
        keep = node.get("level") == "Main Topic" or degree >= 2 or len(retained_nodes) < min(4, max_nodes)
        if keep:
            retained_nodes.append(node)
            if node.get("level") == "Main Topic":
                main_topic_included = True
        if len(retained_nodes) >= max_nodes:
            break

    if not main_topic_included and ranked_nodes:
        retained_nodes = [ranked_nodes[0], *retained_nodes[: max_nodes - 1]]

    retained_ids = {normalize_entity(node["id"]) for node in retained_nodes}
    retained_edges = [
        edge for edge in edges
        if normalize_entity(edge["source"]) in retained_ids and normalize_entity(edge["target"]) in retained_ids
    ]
    retained_edges.sort(
        key=lambda edge: (
            edge.get("confidence", 0.0),
            relation_priority(edge.get("relation", "")),
        ),
        reverse=True,
    )
    retained_edges = retained_edges[:max_relations]

    connected_ids = {
        normalize_entity(edge["source"]) for edge in retained_edges
    } | {
        normalize_entity(edge["target"]) for edge in retained_edges
    }
    retained_nodes = [
        node for node in retained_nodes
        if node.get("level") == "Main Topic" or normalize_entity(node["id"]) in connected_ids
    ]

    return retained_nodes, retained_edges


def sentence_entity_matches(sentence_text: str, entity_records: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized_sentence = sentence_text.lower()
    matches: List[Dict[str, Any]] = []

    for record in entity_records:
        entity_key = normalize_entity(record["id"])
        if entity_key and entity_key in normalized_sentence:
            matches.append(record)

    matches.sort(key=lambda item: sentence_text.lower().find(normalize_entity(item["id"])))
    return matches


def relation_phrase_in_sentence(sentence_text: str) -> Optional[Tuple[str, str]]:
    lowered = sentence_text.lower()
    for phrase, relation in sorted(RELATION_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if phrase in lowered:
            return phrase, relation
    return None


def infer_relation_from_sentence(sentence: Any) -> Optional[Tuple[str, str, Optional[int]]]:
    sentence_text = sentence.text if hasattr(sentence, "text") else str(sentence)
    explicit = relation_phrase_in_sentence(sentence_text)
    if explicit is not None:
        phrase, relation = explicit
        return phrase, relation, sentence_text.lower().find(phrase)

    if sentence is None or not hasattr(sentence, "root"):
        return None

    root = getattr(sentence, "root", None)
    if root is None:
        return None

    lemma = getattr(root, "lemma_", "").lower().strip()
    token_text = getattr(root, "text", "").lower().strip()
    relation = RELATION_MAP.get(lemma) or RELATION_MAP.get(token_text)
    if relation is None:
        return None

    clue = token_text or lemma
    clue_index = sentence_text.lower().find(clue)
    return clue, relation, clue_index if clue_index >= 0 else None


def choose_relation_pair(
    sentence_text: str,
    entity_records: Sequence[Dict[str, Any]],
    phrase: str,
) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
    matches = sentence_entity_matches(sentence_text, entity_records)
    if len(matches) < 2:
        return None

    lowered_sentence = sentence_text.lower()
    phrase_index = lowered_sentence.find(phrase)
    if phrase_index < 0:
        return None

    phrase_end = phrase_index + len(phrase)
    sentence_positions = []
    for record in matches:
        position = lowered_sentence.find(normalize_entity(record["id"]))
        sentence_positions.append((position, record))

    before = [item for item in sentence_positions if item[0] <= phrase_index]
    after = [item for item in sentence_positions if item[0] >= phrase_end]

    if before and after:
        source = max(before, key=lambda item: item[0])[1]
        target = min(after, key=lambda item: item[0])[1]
        if source["id"] != target["id"]:
            return source, target

    first = sentence_positions[0][1]
    second = sentence_positions[1][1]
    if first["id"] == second["id"]:
        return None
    return first, second


def infer_fallback_relation(sentence_text: str) -> str:
    lowered = sentence_text.lower()
    for phrase, relation in FALLBACK_RELATION_HINTS:
        if phrase in lowered:
            return relation
    # Prefer a verb-like fallback over a generic mention label.
    words = re.findall(r"\b[a-z][a-z\-]{2,}\b", lowered)
    for word in words:
        if word in {"say", "says", "said", "report", "reports", "reported"}:
            continue
        if word.endswith(("ed", "ing", "es", "s")):
            return word if word in {"uses", "protects", "affects", "causes"} else word.rstrip("s")
    return "related_to"


def build_relationships(
    text: str,
    entities: Sequence[Dict[str, Any]],
    max_relations: int = 40,
) -> List[Dict[str, Any]]:
    entity_names = [str(entity.get("id", "")).lower() for entity in entities if entity.get("id")]
    sentences = re.split(r"[.!?]+", text.lower())
    edges: List[Dict[str, Any]] = []
    seen = set()

    for sentence_index, sentence in enumerate(sentences):
        sentence_text = sentence.strip()
        if not sentence_text:
            continue

        present: List[str] = []
        for entity in entity_names:
            root = entity.rstrip("s")
            if not root:
                continue
            if re.search(rf"\b{re.escape(root)}s?\b", sentence_text):
                present.append(entity)

        # Keep only unique entities in sentence order
        present = list(dict.fromkeys(present))
        if len(present) < 2:
            continue

        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                source = present[i]
                target = present[j]
                edge_key = tuple(sorted([source, target]))
                if edge_key in seen:
                    continue

                seen.add(edge_key)
                relation = infer_fallback_relation(sentence_text)
                edges.append(
                    {
                        "source": source,
                        "target": target,
                        "relation": relation,
                        "confidence": 0.55,
                        "sentence": sentence_text,
                        "sentence_index": sentence_index,
                    }
                )

                if len(edges) >= max_relations:
                    return edges

    return edges


def build_edges(
    texts: Sequence[str],
    entity_records: Sequence[Dict[str, Any]],
    max_relations: int = MAX_RELATIONS,
) -> Tuple[List[Dict[str, Any]], int]:
    nlp = load_nlp()
    combined_text = " ".join(text for text in texts if text)
    doc = nlp(combined_text) if nlp is not None else None
    edges: List[Dict[str, Any]] = []
    candidate_count = 0
    seen = set()

    for sentence_index, sentence in enumerate(iter_sentences(doc, texts)):
        sentence_text = sentence.text if hasattr(sentence, "text") else str(sentence)
        relation_info = infer_relation_from_sentence(sentence)
        if relation_info is None:
            relation = infer_fallback_relation(sentence_text)
            phrase = relation
        else:
            phrase, relation, relation_position = relation_info
        pair = choose_relation_pair(sentence_text, entity_records, phrase)
        if pair is None:
            continue

        source, target = pair
        if source["id"] == target["id"]:
            continue

        candidate_count += 1
        edge_key = (normalize_entity(source["id"]), normalize_entity(target["id"]), relation)
        if edge_key in seen:
            continue
        seen.add(edge_key)

        source_confidence = float(source.get("confidence", 0.0))
        target_confidence = float(target.get("confidence", 0.0))
        relation_strength = 1.0 if phrase in sentence_text.lower() else 0.75
        relation_boost = 0.0 if relation in {"related_to", "mentions"} else 0.1
        edge_confidence = min(1.0, 0.42 + relation_boost + 0.2 * relation_strength + 0.17 * source_confidence / 10 + 0.17 * target_confidence / 10)

        edges.append(
            {
                "source": source["id"],
                "target": target["id"],
                "relation": relation,
                "confidence": round(edge_confidence, 4),
                "sentence": sentence_text,
                "sentence_index": sentence_index,
            }
        )

    edges.sort(
        key=lambda item: (
            item["confidence"],
            relation_priority(item["relation"]),
            -item["sentence_index"],
        ),
        reverse=True,
    )

    if edges:
        return edges[:max_relations], candidate_count

    fallback_edges = build_relationships(combined_text, entity_records, max_relations=max_relations)
    return fallback_edges[:max_relations], len(fallback_edges)


def graph_metrics(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]], candidate_nodes: int, candidate_relations: int) -> Dict[str, Any]:
    meaningful_nodes = len(nodes)
    total_nodes = candidate_nodes or meaningful_nodes
    valid_relations = len(edges)
    total_relations = candidate_relations or valid_relations

    graph_accuracy = (valid_relations / total_relations * 100) if total_relations else 0.0
    semantic_quality = (meaningful_nodes / total_nodes * 100) if total_nodes else 0.0
    final_graph_score = (0.6 * graph_accuracy) + (0.4 * semantic_quality)

    return {
        "meaningful_nodes": meaningful_nodes,
        "total_nodes": total_nodes,
        "valid_relations": valid_relations,
        "total_relations": total_relations,
        "graph_accuracy": round(graph_accuracy, 2),
        "semantic_quality": round(semantic_quality, 2),
        "final_graph_score": round(final_graph_score, 2),
    }


def build_knowledge_graph(
    relevant_texts: Sequence[str],
    max_nodes: int = MAX_NODES,
    max_relations: int = MAX_RELATIONS,
) -> Dict[str, Any]:
    combined_text = " ".join(text for text in relevant_texts if text)
    entity_records = extract_entity_records(combined_text)
    nodes = build_node_payload(entity_records, max_nodes=max_nodes)
    selected_ids = {normalize_entity(node["id"]) for node in nodes}

    filtered_entity_records = [record for record in entity_records if normalize_entity(record["id"]) in selected_ids]
    edges, candidate_relations = build_edges(relevant_texts, filtered_entity_records, max_relations=max_relations)
    candidate_nodes = len(entity_records)
    pruned_nodes, pruned_edges = prune_graph(nodes, edges, max_nodes=max_nodes, max_relations=max_relations)
    metrics = graph_metrics(pruned_nodes, pruned_edges, candidate_nodes, candidate_relations)

    return {
        "nodes": pruned_nodes,
        "edges": pruned_edges,
        "graph_metrics": metrics,
    }


if __name__ == "__main__":
    sample_text = (
        "The Times of India is owned by Bennett, Coleman & Co. Ltd. "
        "It is headquartered in Mumbai, India and edited by Jaideep Bose."
    )
    print(build_knowledge_graph([sample_text]))
