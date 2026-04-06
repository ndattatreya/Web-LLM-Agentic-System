import re

def segment_text(text: str, min_words=80, max_words=200):
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)

    segments = []
    current = []

    for sentence in sentences:
        if len(sentence.split()) < 5:
            continue

        current.append(sentence)
        word_count = len(" ".join(current).split())

        # Hard split
        if word_count >= max_words:
            segments.append(" ".join(current))
            current = []

        # Soft split at sentence boundary
        elif word_count >= min_words:
            segments.append(" ".join(current))
            current = []

    if current:
        segments.append(" ".join(current))

    return segments
