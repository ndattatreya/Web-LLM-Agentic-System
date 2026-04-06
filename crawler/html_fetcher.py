import requests


def fetch_html(url: str) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml"
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)

        if response.status_code != 200:
            return {
                "error": f"HTTP {response.status_code}",
                "html": ""
            }

        html = response.text.strip()

        # Detect bot-block / JS-only pages
        if len(html) < 500 or "enable javascript" in html.lower():
            return {
                "error": "Blocked by website (anti-bot protection)",
                "html": ""
            }

        return {"html": html}

    except Exception as e:
        return {
            "error": str(e),
            "html": ""
        }
