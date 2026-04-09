import re

# -------------------------------
# CONFIG
# -------------------------------

MIN_WORDS = 30          # ignore very small chunks
MIN_SCORE = 0.15        # minimum relevance score to keep a segment


SECTION_KEYWORDS = {
    "abstract", "introduction", "background",
    "method", "methods", "approach",
    "model", "architecture", "algorithm",
    "experiment", "experiments", "results",
    "evaluation", "analysis", "discussion",
    "conclusion", "limitations", "future work"
}

TECH_KEYWORDS = {
    "model", "data", "learning", "training",
    "algorithm", "optimization", "loss",
    "gradient", "neural", "network",
    "representation", "embedding",
    "inference", "probability", "parameter"
}


# -------------------------------
# HELPERS
# -------------------------------

def normalize(text: str) -> str:
    """Lowercase and remove special characters"""
    return re.sub(r"[^a-z0-9 ]+", " ", text.lower())


def has_academic_signals(text: str) -> bool:
    """Detect citations, figures, tables"""
    return (
        bool(re.search(r"\[\d+\]", text)) or        # [12]
        bool(re.search(r"\(\d{4}\)", text)) or      # (2023)
        bool(re.search(r"\bfig\.|\btable\b", text.lower()))
    )


def has_numeric_signals(text: str) -> bool:
    """
    Detect factual information like:
    years, dates, percentages, money, statistics
    """
    patterns = [
        r"\b(19|20)\d{2}\b",              # years: 2018, 2026
        r"\b\d+(\.\d+)?\s?%\b",           # percentages
        r"\b₹\s?\d+|\$\s?\d+\b",          # currency
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",  # dates
        r"\b\d+\b"                        # any number
    ]
    return any(re.search(p, text) for p in patterns)


# -------------------------------
# MAIN RELEVANCE FUNCTION
# -------------------------------

def is_relevant(text: str):

    if not text or not text.strip():
        return False, 0.0

    words = text.split()
    word_count = len(words)

    # 1️⃣ Length gate
    if word_count < 20:
        return False, 0.0

    clean = normalize(text)
    score = 0.0

    # ✅ 2️⃣ Length quality (VERY IMPORTANT)
    if 40 <= word_count <= 150:
        score += 0.25
    elif 20 <= word_count < 40:
        score += 0.15

    # ✅ 3️⃣ Sentence structure
    sentence_count = text.count(".")
    if sentence_count >= 2:
        score += 0.25

    # ✅ 4️⃣ Vocabulary richness
    unique_ratio = len(set(words)) / word_count
    if unique_ratio > 0.5:
        score += 0.2

    # ✅ 5️⃣ Numeric / factual info
    if has_numeric_signals(text):
        score += 0.2

    # ✅ 6️⃣ Mild keyword (GENERAL, not tech-only)
    general_keywords = [
        "is", "are", "was", "were",
        "species", "system", "process",
        "important", "used", "known"
    ]
    if any(k in clean for k in general_keywords):
        score += 0.1

    # 🚫 Noise penalty
    symbol_ratio = sum(
        1 for c in text if not c.isalnum() and c not in " .,-"
    ) / max(len(text), 1)

    if symbol_ratio > 0.3:
        score -= 0.2

    if "&#" in text or "&amp;" in text:
        score -= 0.2

    # Clamp
    score = max(0.0, min(score, 1.0))

    return score >= 0.3, round(score, 4)