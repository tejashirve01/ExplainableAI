import sys
import os

# Fix path for both local and Docker environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_PATH)

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

import time
import shutil
from backend.src.pdf_loader import load_all_papers
from backend.src.embedder import Embedder
from backend.src.vector_store import VectorStore
from backend.src.search_engine import SearchEngine
from backend.src.answer_generator import AnswerGenerator
from backend.src.explainer import Explainer


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    question: str


# -------- GLOBAL PIPELINE VARIABLES -------- #

search_engine = None
generator = None
explainer = None
pipeline_ready = False

print("Server ready — waiting for document upload.")


# -------- HELPER: BUILD PIPELINE -------- #

def build_pipeline(folder):
    global search_engine, generator, explainer, pipeline_ready

    chunks = load_all_papers(folder)
    texts = [c["chunk"] for c in chunks]

    embedder = Embedder()
    embeddings = embedder.embed(texts)
    dimension = embeddings.shape[1]

    vector_db = VectorStore(dimension)
    vector_db.add_embeddings(embeddings)

    search_engine = SearchEngine(embedder, vector_db, chunks)
    generator = AnswerGenerator()
    explainer = Explainer()
    pipeline_ready = True

    return len(chunks)


# -------- AUTO LOAD IF PAPERS EXIST -------- #

folder = os.path.join(BASE_DIR, "data", "papers")
if os.path.exists(folder) and any(f.endswith(".pdf") for f in os.listdir(folder)):
    print("Found existing papers, loading pipeline...")
    build_pipeline(folder)
    print("Pipeline ready!")


# -------- API ROUTES -------- #

@app.get("/")
def home():
    return {"message": "XAI RAG API running", "pipeline_ready": pipeline_ready}


@app.post("/upload")
def upload_documents(files: List[UploadFile] = File(...)):
    upload_folder = os.path.join(BASE_DIR, "data", "papers")
    os.makedirs(upload_folder, exist_ok=True)

    # Clear old PDFs
    for f in os.listdir(upload_folder):
        if f.endswith(".pdf"):
            os.remove(os.path.join(upload_folder, f))

    # Save new uploaded files
    uploaded_names = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            continue
        dest = os.path.join(upload_folder, file.filename)
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        uploaded_names.append(file.filename)

    if not uploaded_names:
        return {"error": "No valid PDF files uploaded."}

    # Rebuild pipeline
    print(f"Rebuilding pipeline with {len(uploaded_names)} documents...")
    total_chunks = build_pipeline(upload_folder)
    print("Pipeline rebuilt!")

    return {
        "message": f"Successfully uploaded and indexed {len(uploaded_names)} documents",
        "files": uploaded_names,
        "total_chunks": total_chunks
    }


@app.post("/ask")
def ask_question(query: Query):

    if not pipeline_ready:
        return {
            "answer": "No documents uploaded yet. Please upload PDFs first.",
            "confidence": 0.0,
            "reasoning": "",
            "keywords": None,
            "chunks": [],
            "traces": []
        }

    traces = []
    start_total = time.time()

    # Step 1 — Query received
    t0 = time.time()
    question = query.question
    traces.append({
        "step": 1,
        "title": "Query Received",
        "detail": f'User asked: "{question}"',
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 2 — Vector search
    t0 = time.time()
    results = search_engine.search(question)
    traces.append({
        "step": 2,
        "title": "Vector Search",
        "detail": f"Searched vector database using semantic similarity.\nRetrieved {len(results)} matching chunks.",
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 3 — Top chunks selected
    t0 = time.time()
    top_chunks = [
        {
            "text": r["chunk"],
            "source": r.get("source", "unknown"),
            "page": r.get("page", "unknown"),
            "score": float(r["score"])
        }
        for r in results[:3]
    ]
    traces.append({
        "step": 3,
        "title": "Top Chunks Selected",
        "detail": "\n".join([
            f"Chunk {i+1}: {c['source']} | page {c['page']} | score: {c['score']:.4f} | preview: {c['text'][:80]}..."
            for i, c in enumerate(top_chunks)
        ]),
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 4 — LLM generation
    t0 = time.time()
    result = generator.generate_with_reasoning(question, results)
    answer = result["answer"]
    traces.append({
        "step": 4,
        "title": "LLM Generation",
        "detail": f"Sent {len(results)} chunks as context to Gemini 2.5 Flash.\nModel generated answer + reasoning + confidence level.",
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 5 — Answer check
    t0 = time.time()
    if "cannot find the answer" in answer.lower():
        traces.append({
            "step": 5,
            "title": "Answer Check",
            "detail": "Answer not found in the retrieved documents.\nReturning fallback response.",
            "duration_ms": round((time.time() - t0) * 1000, 2)
        })
        traces.append({
            "step": 6,
            "title": "Pipeline Complete",
            "detail": f"Total pipeline time: {round((time.time() - start_total) * 1000, 2)}ms\nResult: No answer found.",
            "duration_ms": round((time.time() - start_total) * 1000, 2)
        })
        return {
            "answer": answer,
            "confidence": 0.0,
            "reasoning": "No relevant chunks found in the documents.",
            "keywords": None,
            "chunks": [],
            "traces": traces
        }

    traces.append({
        "step": 5,
        "title": "Answer Check",
        "detail": "Answer successfully found in the retrieved documents. Proceeding to confidence calculation.",
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 6 — Confidence calculation
    t0 = time.time()
    scores = [float(r["score"]) for r in results]
    numeric_confidence = round(sum(scores) / len(scores), 4)
    traces.append({
        "step": 6,
        "title": "Confidence Calculation",
        "detail": f"Chunk scores: {[round(s, 4) for s in scores]}\nAverage confidence: {numeric_confidence}  |  LLM confidence level: {result['confidence_level']}",
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 7 — Keyword extraction
    t0 = time.time()
    keywords = explainer.extract_keywords(results)
    traces.append({
        "step": 7,
        "title": "Keyword Extraction",
        "detail": f"Extracted {len(keywords) if keywords else 0} keywords from retrieved chunks:\n{', '.join(keywords) if keywords else 'none'}",
        "duration_ms": round((time.time() - t0) * 1000, 2)
    })

    # Step 8 — Pipeline complete
    total_ms = round((time.time() - start_total) * 1000, 2)
    traces.append({
        "step": 8,
        "title": "Pipeline Complete",
        "detail": f"All components assembled successfully.\nTotal pipeline time: {total_ms}ms",
        "duration_ms": total_ms
    })

    return {
        "answer": answer,
        "confidence": float(numeric_confidence),
        "confidence_level": result["confidence_level"],
        "reasoning": result["reasoning"],
        "keywords": keywords,
        "chunks": top_chunks,
        "traces": traces
    }