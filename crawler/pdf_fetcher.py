import io
import requests
import pdfplumber


def fetch_pdf(file_path: str) -> dict:
    # Local file
    if not file_path.startswith("http"):
        with pdfplumber.open(file_path) as pdf:
            pages = [
                page.extract_text()
                for page in pdf.pages
                if page.extract_text()
            ]
    else:
        # URL PDF
        response = requests.get(file_path, timeout=30)
        response.raise_for_status()

        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            pages = [
                page.extract_text()
                for page in pdf.pages
                if page.extract_text()
            ]

    return {
        "source_type": "pdf",
        "source_id": file_path,
        "text": "\n".join(pages)
    }
