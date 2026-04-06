"""
FastAPI Backend for Web-LLM Agentic System
Provides REST API endpoints for document processing, relevance filtering, and model comparison
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile

# Add parent directory to path to import project modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from crawler.document_loader import load_document
from agent.content_extractor import extract_main_content
from agent.pdf_cleaner import clean_pdf_text
from classifier.relevance_model_inference import is_relevant_ml
from agent.model_comparator import compare_models
from agent.confidence_scorer import score_relevance

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
RESULTS_DIR = Path(__file__).parent.parent.parent / "data" / "api_results"
RESULTS_DIR.mkdir(exist_ok=True)

processing_results = {}

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

@app.post("/process/url", response_model=ProcessingResult, tags=["Processing"])
async def process_url(url: str):
    """
    Process a URL and extract relevant segments
    
    Args:
        url: The URL to process
    
    Returns:
        ProcessingResult with segments and analysis
    """
    import time
    start_time = time.time()
    
    try:
        # Load document from URL
        print(f"Loading URL: {url}")
        doc = load_document(url)
        
        raw_text = doc.get("text", "")
        if isinstance(raw_text, dict):
            raw_text = raw_text.get("html", "")
        
        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from URL")
        
        # Extract main content
        print("Extracting main content...")
        extracted = extract_main_content(raw_text)
        text = extracted if isinstance(extracted, str) else raw_text
        
        # Split into segments
        segments = split_text(text)
        
        # Filter relevant segments
        print(f"Filtering {len(segments)} segments...")
        relevant_segments = []
        for idx, seg in enumerate(segments):
            try:
                is_relevant = is_relevant_ml(seg)
                score = score_relevance(seg)
                if is_relevant:
                    relevant_segments.append({
                        "id": f"seg_{idx}",
                        "text": seg,
                        "is_relevant": True,
                        "relevance_score": score.get("score", 0.0),
                        "confidence": score.get("confidence", 0.0)
                    })
            except Exception as e:
                print(f"Error processing segment {idx}: {e}")
                continue
        
        processing_time = time.time() - start_time
        
        result = {
            "source": url,
            "source_type": "url",
            "raw_text": text[:1000] + ("..." if len(text) > 1000 else ""),
            "total_segments": len(segments),
            "relevant_segments": relevant_segments,
            "entities": [],
            "key_points": [],
            "processing_time": processing_time
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.post("/process/file", response_model=ProcessingResult, tags=["Processing"])
async def process_file(file: UploadFile = File(...)):
    """
    Process an uploaded file (PDF, audio, etc.)
    
    Args:
        file: The file to process
    
    Returns:
        ProcessingResult with segments and analysis
    """
    import time
    start_time = time.time()
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            # Load document
            print(f"Loading file: {file.filename}")
            doc = load_document(tmp_path)
            
            raw_text = doc.get("text", "")
            if isinstance(raw_text, dict):
                raw_text = raw_text.get("html", "")
            
            if not raw_text:
                raise HTTPException(status_code=400, detail="Could not extract text from file")
            
            # Extract main content (especially for PDF)
            if tmp_path.endswith('.pdf'):
                print("Cleaning PDF text...")
                text = clean_pdf_text(raw_text)
            else:
                text = extract_main_content(raw_text) if isinstance(raw_text, str) else raw_text
            
            # Split into segments
            segments = split_text(text)
            
            # Filter relevant segments
            print(f"Filtering {len(segments)} segments...")
            relevant_segments = []
            for idx, seg in enumerate(segments):
                try:
                    is_relevant = is_relevant_ml(seg)
                    score = score_relevance(seg)
                    if is_relevant:
                        relevant_segments.append({
                            "id": f"seg_{idx}",
                            "text": seg,
                            "is_relevant": True,
                            "relevance_score": score.get("score", 0.0),
                            "confidence": score.get("confidence", 0.0)
                        })
                except Exception as e:
                    print(f"Error processing segment {idx}: {e}")
                    continue
            
            processing_time = time.time() - start_time
            
            result = {
                "source": file.filename,
                "source_type": "file",
                "raw_text": text[:1000] + ("..." if len(text) > 1000 else ""),
                "total_segments": len(segments),
                "relevant_segments": relevant_segments,
                "entities": [],
                "key_points": [],
                "processing_time": processing_time
            }
            
            return result
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

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
