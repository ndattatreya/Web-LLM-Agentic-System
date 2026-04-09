"""
FastAPI Backend for Web-LLM Agentic System
Provides REST API endpoints for document processing, relevance filtering, and model comparison
"""

import os

os.environ["PATH"] += os.pathsep + r"C:\Users\NAMMINA JAHNAVI\Downloads\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin"
import sys
import json
import re
import asyncio
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import tempfile
import whisper

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from classifier.relevance_filter import is_relevant
from crawler.document_loader import load_document
from agent.content_extractor import extract_main_content
from agent.pdf_cleaner import clean_pdf_text
from agent.model_comparator import compare_models

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

whisper_model = None

# ==========================================
# MODELS
# ==========================================
class ProcessingStatus(BaseModel):
    status: str
    progress: int
    message: str
    current_step: str

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
    total_segments: int
    relevant_segments: List[Segment]
    entities: List[str] = []
    key_points: List[str] = []
    processing_time: float

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

# ==========================================
# STORAGE
# ==========================================
RESULTS_DIR = Path(__file__).parent.parent / "data" / "api_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

processing_results = {}
RELEVANCE_THRESHOLD = 0.6
MAX_RELEVANT_SEGMENTS = 500

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


def keyword_similarity(text: str, query: str) -> float:
    if not query:
        return 0.0

    query_keywords = set(extract_keywords(query))
    text_keywords = set(extract_keywords(text))

    if not query_keywords or not text_keywords:
        return 0.0

    overlap = len(query_keywords & text_keywords)
    return overlap / len(query_keywords)


def get_source_query(source: str) -> str:
    if source.startswith("http"):
        parsed = urlparse(source)
        path = parsed.path or parsed.netloc
        return Path(path).stem.replace("-", " ").replace("_", " ")

    return Path(source).stem.replace("-", " ").replace("_", " ")


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

@app.post("/process/file", response_model=ProcessingResult, tags=["Processing"])
async def process_file(file: UploadFile = File(...)):
    import time
    import numpy as np

    start_time = time.time()

    try:
        print(f"Processing file: {file.filename}")

        # 1️⃣ Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # 2️⃣ LOAD TEXT BASED ON FILE TYPE
            if tmp_path.endswith(".pdf"):
                print("Cleaning PDF...")
                doc = await asyncio.to_thread(load_document, tmp_path)
                raw_text = doc.get("text", "")
                text = await asyncio.to_thread(clean_pdf_text, raw_text)

            elif tmp_path.endswith((".txt", ".md")):
                with open(tmp_path, "r", encoding="utf-8") as f:
                    text = f.read()

            # 🎧 NEW: AUDIO SUPPORT
            elif tmp_path.endswith((".mp3", ".wav", ".m4a", ".aac")):
                print("Transcribing audio...")

                import os
                import whisper

                # 🔥 FORCE FFmpeg PATH (CRITICAL FIX)
                os.environ["PATH"] += os.pathsep + r"C:\Users\NAMMINA JAHNAVI\Downloads\ffmpeg-8.1-essentials_build\ffmpeg-8.1-essentials_build\bin"

                # 🔥 Use smaller model for speed
                model = whisper.load_model("base")

                result = model.transcribe(tmp_path)

                text = result.get("text", "")

                if not text or len(text.strip()) < 10:
                    raise HTTPException(status_code=400, detail="Audio transcription failed")

                print("Audio transcription completed")

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file type (PDF, TXT, AUDIO supported)"
                )
            if not text or len(text.strip()) < 50:
                raise HTTPException(status_code=400, detail="File has insufficient content")

            # 3️⃣ SEGMENT
            segments = split_text(text)
            source_query = get_source_query(file.filename)

            print(f"Segments created: {len(segments)}")

            scored_segments = []

            # 4️⃣ SCORING (NO ML DEPENDENCY)
            for idx, seg in enumerate(segments):
                try:
                    query_score = keyword_similarity(seg, source_query)
                    length_score = min(len(seg.split()) / 50, 1.0)
                    has_numbers = any(char.isdigit() for char in seg)
                    structure_score = 0.2 if has_numbers else 0.0

                    combined_score = (
                        0.4 * query_score +
                        0.4 * length_score +
                        0.2 * structure_score
                    )

                    scored_segments.append({
                        "id": f"seg_{idx}",
                        "text": seg,
                        "is_relevant": False,
                        "relevance_score": round(query_score, 4),
                        "confidence": round(combined_score, 4)
                    })

                except Exception as e:
                    print(f"Error segment {idx}: {e}")
                    continue

            # 5️⃣ DYNAMIC THRESHOLD
            scores = [seg["confidence"] for seg in scored_segments]

            if not scores:
                threshold = 0.4
            else:
                threshold = max(0.35, float(np.percentile(scores, 60)))

            print(f"Dynamic threshold: {threshold}")

            # 6️⃣ FILTER
            relevant_segments = [
                {**seg, "is_relevant": True}
                for seg in scored_segments
                if seg["confidence"] >= threshold
            ]

            relevant_segments = sorted(
                relevant_segments,
                key=lambda x: x["confidence"],
                reverse=True
            )

            print(f"Relevant segments: {len(relevant_segments)}")

            processing_time = time.time() - start_time

            return {
                "source": file.filename,
                "source_type": "file",
                "raw_text": text[:1000],
                "total_segments": len(segments),
                "relevant_segments": relevant_segments,
                "entities": [],
                "key_points": [],
                "processing_time": processing_time
            }

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

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
