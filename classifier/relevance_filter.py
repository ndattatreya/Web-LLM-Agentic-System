from __future__ import annotations

import math
import re
from typing import Any, Dict, List, Sequence

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


MIN_WORDS = 20
MIN_CONFIDENCE = 0.15
KEYWORD_WEIGHT = 0.25
SEMANTIC_WEIGHT = 0.45
STRUCTURAL_WEIGHT = 0.20
POSITION_WEIGHT = 0.10

SECTION_KEYWORDS = {
    "abstract", "introduction", "background",
    "method", "methods", "approach",
    "model", "architecture", "algorithm",
    "experiment", "experiments", "results",
    "evaluation", "analysis", "discussion",
    "conclusion", "limitations", "future work"
}


def normalize(text: str) -> str:
    """Lowercase text and strip punctuation used for overlap scoring."""
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower()).strip()


def extract_keywords(text: str) -> List[str]:
    normalized = normalize(text)
    return [word for word in normalized.split() if len(word) > 3]


def has_numeric_signals(text: str) -> bool:
    patterns = [
        r"\b(19|20)\d{2}\b",
        r"\b\d+(\.\d+)?\s?%\b",
        r"\b₹\s?\d+|\$\s?\d+\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b\d+\b",
    ]
    return any(re.search(pattern, text) for pattern in patterns)


def has_heading_structure(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    return bool(
        re.match(r"^(\d+([.\-]\d+)*)\s+[A-Z]", stripped)
        or re.match(r"^[A-Z][A-Z0-9\s,:\-/()]{4,}$", stripped)
        or (len(stripped.split()) <= 12 and stripped[:1].isupper())
    )


def keyword_similarity(text: str, reference: str) -> float:
    if not text or not reference:
        return 0.0

    text_keywords = set(extract_keywords(text))
    reference_keywords = set(extract_keywords(reference))

    if not text_keywords or not reference_keywords:
        return 0.0

    overlap = len(text_keywords & reference_keywords)
    return round(overlap / len(reference_keywords), 4)


def semantic_similarity(text: str, reference: str) -> float:
    if not text or not reference:
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 3),
            max_features=5000
        )

        matrix = vectorizer.fit_transform([text[:2000], reference[:2000]])
        score = cosine_similarity(matrix[0], matrix[1])[0][0]

        return round(float(score), 4)

    except Exception:
        return 0.0


def position_score(index: int, total: int) -> float:
    if total <= 1:
        return 1.0
    return round(1.0 - (index / max(total - 1, 1)), 4)


def structural_score(text: str, index: int, total: int, input_type: str = "text") -> float:
    score = 0.0
    words = text.split()
    word_count = len(words)

    if 30 <= word_count <= 150:
        score += 0.35
    elif 15 <= word_count < 30:
        score += 0.2

    if has_numeric_signals(text):
        score += 0.2

    if has_heading_structure(text):
        score += 0.25

    if input_type == "pdf":
        if has_heading_structure(text) or text.count("\n") >= 1:
            score += 0.15
    elif input_type == "audio":
        if re.search(r"\b\d{1,2}:\d{2}(?::\d{2})?\b", text):
            score += 0.2
        repeated_terms = max((words.count(word) for word in set(words)), default=0)
        if repeated_terms >= 2:
            score += 0.1
    elif input_type == "url":
        if "title" in normalize(text) or "metadata" in normalize(text):
            score += 0.1

    if total > 1 and index == 0:
        score += 0.1

    return round(min(score, 1.0), 4)


def score_segment(
    text: str,
    reference_text: str = "",
    source_hint: str = "",
    index: int = 0,
    total: int = 1,
    input_type: str = "text",
) -> Dict[str, Any]:
    if not text or len(text.split()) < MIN_WORDS:
        return {
            "is_relevant": False,
            "relevance_score": 0.0,
            "confidence": 0.0,
        }

    combined_reference = " ".join(part for part in [source_hint, reference_text] if part).strip()

    keyword_score = keyword_similarity(text, combined_reference)
    semantic_score = semantic_similarity(text, combined_reference)
    structural = structural_score(text, index, total, input_type=input_type)
    positional = position_score(index, total)

    combined = (
        KEYWORD_WEIGHT * keyword_score
        + SEMANTIC_WEIGHT * semantic_score
        + STRUCTURAL_WEIGHT * structural
        + POSITION_WEIGHT * positional
    )

    confidence = round(max(0.0, min(combined, 1.0)), 4)

    return {
        "is_relevant": confidence >= MIN_CONFIDENCE,
        "relevance_score": confidence,
        "confidence": confidence,
        "score_breakdown": {
            "keyword_similarity": keyword_score,
            "semantic_similarity": semantic_score,
            "structural_score": structural,
            "position_score": positional,
        },
    }


def rank_segments(
    segments: Sequence[str],
    reference_text: str = "",
    source_hint: str = "",
    input_type: str = "text",
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    _ = top_k  # Kept for API compatibility.
    total = len(segments)
    scored_segments: List[Dict[str, Any]] = []

    for index, segment in enumerate(segments):
        score = score_segment(
            segment,
            reference_text=reference_text,
            source_hint=source_hint,
            index=index,
            total=total,
            input_type=input_type,
        )

        scored_segments.append(
            {
                "id": f"seg_{index}",
                "text": segment,
                **score,
            }
        )

    scored_segments.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    max_confidence = max((seg["confidence"] for seg in scored_segments), default=0.0)
    min_coverage_count = math.ceil(total * 0.40)
    target_coverage_count = math.ceil(total * 0.50)
    min_required = min_coverage_count
    if total >= 20:
        min_required = max(10, min_coverage_count)

    absolute_floor = min(total, 10) if total >= 20 else min_required

    # Start strict and progressively relax if selected segments are too few.
    threshold_factors = [0.45, 0.35, 0.25]
    adaptive_threshold = 0.0
    relevant_segments: List[Dict[str, Any]] = []

    for factor in threshold_factors:
        adaptive_threshold = max_confidence * factor
        relevant_segments = [
            seg for seg in scored_segments
            if seg["confidence"] >= adaptive_threshold
        ]

        if len(relevant_segments) >= min_required:
            break

        # If fewer than 10 are selected, lower threshold and retry.
        if len(relevant_segments) >= absolute_floor:
            break

    # Guarantee at least 40% coverage (and at least 10 when available).
    if len(relevant_segments) < min_required:
        relevant_segments = scored_segments[:min_required]

    # Keep output within a practical upper band when possible.
    if min_required <= target_coverage_count and len(relevant_segments) > target_coverage_count:
        relevant_segments = relevant_segments[:target_coverage_count]

    return {
        "total_segments": total,
        "relevant_count": len(relevant_segments),
        "coverage_percent": round((len(relevant_segments) / total) * 100, 2) if total else 0,
        "relevant_segments": relevant_segments
    }


def is_relevant(text: str):
    if not text or not text.strip():
        return False, 0.0

    result = score_segment(text, reference_text="", source_hint="", index=0, total=1, input_type="text")
    return bool(result["is_relevant"]), round(float(result["confidence"]), 4)