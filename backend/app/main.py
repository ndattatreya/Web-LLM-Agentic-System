import os

os.environ["PATH"] += os.pathsep + r"C:\Users\NAMMINA JAHNAVI\Downloads\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin"
import sys
import json
import re
import asyncio
import time
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import tempfile

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawler.document_loader import load_document
from classifier.relevance_filter import rank_segments
from agent.knowledge_representation import build_knowledge_graph

# ==========================================
# CONFIG
# ==========================================
app = FastAPI(
    title="Web-LLM Agentic System API",
    description="API for document processing, relevance filtering, and model comparison",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MODELS
# ==========================================

class Segment(BaseModel):
    id: str
    text: str
    is_relevant: bool
    relevance_score: Optional[float] = None
    confidence: Optional[float] = None

class ProcessingResult(BaseModel):
    source: str
    source_type: str
    raw_text: str
    extracted_text: Optional[str] = None
    total_segments: int
    relevant_count: int
    coverage_percent: float
    relevant_segments: List[Segment]
    entities: List[str] = []
    key_points: List[str] = []
    processing_time: float
    framework_output: Optional[dict] = None
    knowledge_graph: Optional[dict] = None
    comparison: Optional[dict] = None

class ModelComparison(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    model_a: str
    model_b: str
    total_comparisons: int
    model_a_avg_time: float
    model_b_avg_time: float
    faster_model: str
    time_difference_percent: float

class DatasetStatistics(BaseModel):
    total_samples: int
    relevant_count: int
    irrelevant_count: int
    relevant_percentage: float

class GraphRequest(BaseModel):
    text: str
    max_nodes: Optional[int] = 12
    max_relations: Optional[int] = 10

# ==========================================
# STORAGE
# ==========================================
RESULTS_DIR = Path(__file__).parent.parent / "data" / "api_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# UTILITY FUNCTIONS
# ==========================================
def split_text(text: str, max_words: int = 50) -> List[str]:
    """Split text into segments by word count"""
    words = text.split()
    return [
        " ".join(words[i:i + max_words])
        for i in range(0, len(words), max_words)
    ]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return " ".join(text.split())


def extract_keywords(text: str) -> List[str]:
    normalized = normalize_text(text)
    return [word for word in normalized.split() if len(word) > 3]


def get_source_query(source: str) -> str:
    if source.startswith("http"):
        parsed = urlparse(source)
        path = parsed.path or parsed.netloc
        return Path(path).stem.replace("-", " ").replace("_", " ")

    return Path(source).stem.replace("-", " ").replace("_", " ")


def build_reference_context(source_hint: str, text: str) -> str:
    """Build rich reference context by combining source hint with text keywords.
    
    This helps the relevance filter compare segments against meaningful context
    instead of empty strings, improving similarity scoring significantly.
    """
    # Start with source hint
    context_parts = [source_hint]
    
    # Extract first 800 chars for beginning-of-document context
    text_snippet = text[:800].strip()
    if text_snippet:
        context_parts.append(text_snippet)
    
    # Extract top keywords from the text (up to 30)
    all_keywords = extract_keywords(text)
    top_keywords = list(set(all_keywords))[:30]  # Deduplicate and limit
    if top_keywords:
        context_parts.append(" ".join(top_keywords))
    
    return " ".join(context_parts)


def clean_web_text(text: str) -> str:
    if not text:
        return ""

    # Remove citation markers such as [1], [a], [note 1]
    text = re.sub(r"\[(?:\d+|[a-zA-Z]+|note\s*\d+)\]", "", text, flags=re.IGNORECASE)

    # Remove stacked bracket fragments that often remain after scraping
    text = re.sub(r"(\[\s*.*?\s*\])+", "", text)

    # Normalize non-breaking spaces and punctuation spacing
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    text = re.sub(r"([.,;:!?]){2,}", r"\1", text)

    # Normalize whitespace and remove spaces before punctuation
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)

    # Split badly joined camel-case style sentence boundaries
    text = re.sub(r"([a-z])([A-Z])", r"\1. \2", text)

    return text.strip()


def polish_sentence(text: str) -> str:
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)
    cleaned: List[str] = []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
        if sentence[-1] not in ".!?":
            sentence += "."
        cleaned.append(sentence)

    return " ".join(cleaned)


def build_framework_output(relevant_segments: List[dict], nodes: List[dict], edges: List[dict], graph_metrics: dict, processing_time: float) -> dict:
    return {
        "segments": [
            int(seg["id"].replace("seg_", "")) + 1
            for seg in relevant_segments
        ],
        "summary": " ".join(seg["text"] for seg in relevant_segments[:3])[:500],
        "nodes": nodes,
        "edges": edges,
        "graph_metrics": graph_metrics,
        "time": processing_time,
    }


def build_processing_result_payload(
    source: str,
    source_type: str,
    text: str,
    source_hint: str,
    input_type: str,
    start_time: float,
) -> dict:
    segments = split_text(text)
    reference_text = build_reference_context(source_hint, text)

    ranking_result = rank_segments(
        segments,
        reference_text=reference_text,
        source_hint=source_hint,
        input_type=input_type,
        top_k=5,
    )

    relevant_segments = ranking_result["relevant_segments"]
    total_segments = ranking_result["total_segments"]
    relevant_count = ranking_result["relevant_count"]
    coverage_percent = ranking_result["coverage_percent"]

    processing_time = round(time.time() - start_time, 2)

    graph = build_knowledge_graph([seg["text"] for seg in relevant_segments])
    nodes = graph["nodes"]
    edges = graph["edges"]
    graph_metrics = graph.get("graph_metrics", {})

    framework_output = build_framework_output(
        relevant_segments,
        nodes,
        edges,
        graph_metrics,
        processing_time,
    )

    return {
        "source": source,
        "source_type": source_type,
        "raw_text": text[:1000],
        "extracted_text": text,
        "total_segments": total_segments,
        "relevant_count": relevant_count,
        "coverage_percent": coverage_percent,
        "relevant_segments": relevant_segments,
        "entities": [node["id"] for node in nodes],
        "key_points": [
            seg["text"][:120]
            for seg in relevant_segments[:5]
        ],
        "processing_time": processing_time,
        "framework_output": framework_output,
        "knowledge_graph": graph,
    }


def save_result(result_id: str, data: dict):
    """Save processing result to file"""
    result_file = RESULTS_DIR / f"{result_id}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_result(result_id: str) -> Optional[dict]:
    """Load processing result from file"""
    result_file = RESULTS_DIR / f"{result_id}.json"
    if result_file.exists():
        with open(result_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# ==========================================
# API ENDPOINTS
# ==========================================
@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Web-LLM Agentic System API is running",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/graph/analyze", tags=["Graph"])
async def analyze_graph(payload: GraphRequest):
    """Build a semantic knowledge graph from extracted text"""
    try:
        graph = build_knowledge_graph(
            [payload.text],
            max_nodes=payload.max_nodes or 12,
            max_relations=payload.max_relations or 10,
        )

        return {
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
            "graph_metrics": graph.get("graph_metrics", {}),
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error analyzing graph: {str(error)}")

@app.post("/process/file", response_model=ProcessingResult, tags=["Processing"])
async def process_file(file: UploadFile = File(...)):
    import os

    start_time = time.time()

    try:
        print(f"Processing file: {file.filename}")

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # --------------------------------
            # LOAD TEXT
            # --------------------------------
            if tmp_path.endswith(".pdf"):
                from agent.pdf_cleaner import clean_pdf_text

                doc = await asyncio.to_thread(load_document, tmp_path)
                raw_text = doc.get("text", "")
                text = await asyncio.to_thread(clean_pdf_text, raw_text)

            elif tmp_path.endswith((".txt", ".md")):
                with open(tmp_path, "r", encoding="utf-8") as f:
                    text = f.read()

            elif tmp_path.endswith((".mp3", ".wav", ".m4a", ".aac")):
                whisper = __import__("whisper")

                model = whisper.load_model("base")
                result = model.transcribe(tmp_path)
                text = result.get("text", "")

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type"
                )

            if not text or len(text.strip()) < 50:
                raise HTTPException(
                    status_code=400,
                    detail="File has insufficient content"
                )

            source_hint = get_source_query(file.filename)
            input_type = "pdf" if tmp_path.endswith(".pdf") else "audio" if tmp_path.endswith((".mp3", ".wav", ".m4a", ".aac")) else "text"
            return build_processing_result_payload(
                source=file.filename,
                source_type="file",
                text=text,
                source_hint=source_hint,
                input_type=input_type,
                start_time=start_time,
            )

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process/url", response_model=ProcessingResult, tags=["Processing"])
async def process_url(url: str):
    start_time = time.time()

    try:
        # --------------------------------
        # FETCH CONTENT
        # --------------------------------
        if url.endswith(".pdf"):
            from crawler.pdf_fetcher import fetch_pdf
            from agent.pdf_cleaner import clean_pdf_text

            doc = await asyncio.to_thread(fetch_pdf, url)
            text = doc.get("text", "")
            text = await asyncio.to_thread(clean_pdf_text, text)
            text = polish_sentence(clean_web_text(text))

        else:
            from crawler.html_fetcher import fetch_html
            from agent.content_extractor import extract_main_content

            result = await asyncio.to_thread(fetch_html, url)

            if result.get("error"):
                raise HTTPException(
                    status_code=400,
                    detail=result.get("error")
                )

            text = await asyncio.to_thread(
                extract_main_content,
                result.get("html", "")
            )
            text = polish_sentence(clean_web_text(text))

        if not text or len(text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="URL has insufficient content"
            )

        source_hint = get_source_query(url)
        return build_processing_result_payload(
            source=url,
            source_type="url",
            text=text,
            source_hint=source_hint,
            input_type="url",
            start_time=start_time,
        )

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/data/dataset", response_model=DatasetStatistics, tags=["Data"])
async def get_dataset_statistics():
    """Get dataset statistics"""
    try:
        dataset_path = Path(__file__).parent.parent.parent / "data" / "dataset.json"
        
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
        
        total = len(dataset)
        relevant = sum(1 for item in dataset if item.get("label") == 1)
        irrelevant = total - relevant
        
        return {
            "total_samples": total,
            "relevant_count": relevant,
            "irrelevant_count": irrelevant,
            "relevant_percentage": (relevant / total * 100) if total > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading dataset: {str(e)}")

@app.get("/data/model-comparison", response_model=List[dict], tags=["Data"])
async def get_model_comparison():
    """Get model comparison results"""
    try:
        comparison_path = Path(__file__).parent.parent.parent / "data" / "results" / "model_comparison.json"
        
        with open(comparison_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading model comparison: {str(e)}")

@app.get("/data/model-comparison/summary", response_model=ModelComparison, tags=["Data"])
async def get_model_comparison_summary():
    """Get aggregated model comparison summary"""
    try:
        comparison_path = Path(__file__).parent.parent.parent / "data" / "results" / "model_comparison.json"
        
        with open(comparison_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        model_a_times = []
        model_b_times = []
        
        for item in data:
            if "model_a" in item and "inference_time_sec" in item["model_a"]:
                model_a_times.append(item["model_a"]["inference_time_sec"])
            if "model_b" in item and "inference_time_sec" in item["model_b"]:
                model_b_times.append(item["model_b"]["inference_time_sec"])
        
        avg_a = sum(model_a_times) / len(model_a_times) if model_a_times else 0
        avg_b = sum(model_b_times) / len(model_b_times) if model_b_times else 0
        
        faster = "Model A" if avg_a < avg_b else "Model B"
        time_diff = abs(avg_a - avg_b) / max(avg_a, avg_b) * 100 if max(avg_a, avg_b) > 0 else 0
        
        return {
            "model_a": data[0]["model_a"]["name"] if data else "distilbert",
            "model_b": data[0]["model_b"]["name"] if data else "bert",
            "total_comparisons": len(data),
            "model_a_avg_time": avg_a,
            "model_b_avg_time": avg_b,
            "faster_model": faster,
            "time_difference_percent": time_diff
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.get("/results", tags=["Results"])
async def list_results():
    """List all processing results"""
    try:
        results = []
        if RESULTS_DIR.exists():
            for file in RESULTS_DIR.glob("*.json"):
                results.append({
                    "id": file.stem,
                    "filename": file.name
                })
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing results: {str(e)}")

@app.get("/results/{result_id}", tags=["Results"])
async def get_result(result_id: str):
    """Get a specific processing result"""
    result = load_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
