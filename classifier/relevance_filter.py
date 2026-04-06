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
    """
    Hybrid relevance filter.
    Works well for:
    - PDFs
    - Web articles
    - News
    - Audio transcripts
    """

    if not text or not text.strip():
        return False, 0.0

    words = text.split()
    word_count = len(words)

    # 1️⃣ Length gate
    if word_count < MIN_WORDS:
        return False, 0.0

    clean = normalize(text)
    score = 0.0

    # 2️⃣ Section header boost (PDF-friendly)
    for sec in SECTION_KEYWORDS:
        if sec in clean[:200]:
            score += 0.35
            break

    # 3️⃣ Technical keyword density
    tech_hits = sum(1 for kw in TECH_KEYWORDS if kw in clean)
    score += min(tech_hits * 0.05, 0.40)

    # 4️⃣ Academic signals
    if has_academic_signals(text):
        score += 0.20

    # 5️⃣ Numeric / factual importance (NEW)
    if has_numeric_signals(text):
        score += 0.30

    # 6️⃣ Penalize noisy / garbage segments
    symbol_ratio = sum(
        1 for c in text if not c.isalnum() and c not in " .,-"
    ) / max(len(text), 1)

    if symbol_ratio > 0.25:
        score -= 0.20

    # 🚫 HTML entity noise penalty
    if "&#" in text or "&amp;" in text:
        score -= 0.25


    # Clamp score
    score = max(0.0, min(score, 1.0))

    return score >= MIN_SCORE, round(score, 4)
