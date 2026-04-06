import re


def clean_pdf_text(text: str) -> str:
    if not text:
        return ""

    # Fix joined words (basic heuristic)
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove page headers / footers
    text = re.sub(
        r"Published in .*?\(\d{4}\)",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove figure/table captions
    text = re.sub(r"Figure\s+\d+[:.].*?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"Table\s+\d+[:.].*?", "", text, flags=re.IGNORECASE)

    # Remove reference-heavy lines
    text = re.sub(r"\[[0-9,\s]+\]", "", text)

    # Remove long non-language sequences
    text = re.sub(r"\b[a-z]{15,}\b", "", text)

    return text.strip()
