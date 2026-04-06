import re
import html


# -------------------------------
# BASIC HTML CLEANING
# -------------------------------
def strip_html(html_text: str) -> str:
    if not html_text:
        return ""

    # Decode HTML entities like &#x27;
    html_text = html.unescape(html_text)

    # Remove scripts, styles, nav, footer, header
    html_text = re.sub(r"<script.*?>.*?</script>", "", html_text, flags=re.DOTALL | re.I)
    html_text = re.sub(r"<style.*?>.*?</style>", "", html_text, flags=re.DOTALL | re.I)
    html_text = re.sub(r"<nav.*?>.*?</nav>", "", html_text, flags=re.DOTALL | re.I)
    html_text = re.sub(r"<footer.*?>.*?</footer>", "", html_text, flags=re.DOTALL | re.I)
    html_text = re.sub(r"<header.*?>.*?</header>", "", html_text, flags=re.DOTALL | re.I)

    # Convert block tags to newlines
    html_text = re.sub(r"</p>|</div>|</article>|</section>", "\n\n", html_text)
    html_text = re.sub(r"<br\s*/?>", "\n", html_text)

    # Remove all remaining tags
    html_text = re.sub(r"<[^>]+>", " ", html_text)

    # Normalize whitespace
    html_text = re.sub(r"\n\s*\n+", "\n\n", html_text)
    html_text = re.sub(r"[ \t]+", " ", html_text)

    return html_text.strip()


# -------------------------------
# MAIN CONTENT EXTRACTION
# -------------------------------
def extract_main_content(html_text: str) -> str:
    """
    Extracts article-like content from noisy webpages (BBC, NDTV, Medium).
    No ML, no LLM, heuristic-only.
    """

    cleaned = strip_html(html_text)
    if not cleaned:
        return ""

    paragraphs = cleaned.split("\n\n")

    main_paragraphs = []

    for p in paragraphs:
        p = p.strip()
        words = p.split()

        # 1️⃣ Length gate
        if len(words) < 20:
            continue

        # 2️⃣ Drop navigation-style text
        nav_keywords = {
            "home", "news", "sport", "business", "technology",
            "culture", "audio", "video", "live", "weather",
            "languages", "sign in", "register"
        }

        nav_hits = sum(1 for w in nav_keywords if w in p.lower())
        if nav_hits >= 3:
            continue

        # 3️⃣ Drop language lists
        if re.search(r"\b(hindi|arabic|french|urdu|telugu|tamil|spanish)\b", p.lower()):
            continue

        main_paragraphs.append(p)

    return "\n\n".join(main_paragraphs)
