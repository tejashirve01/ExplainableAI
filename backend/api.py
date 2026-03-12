from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")

sys.path.append(SRC_PATH)

from pdf_loader import load_all_papers
from embedder import Embedder
from vector_store import VectorStore
from search_engine import SearchEngine
from answer_generator import AnswerGenerator
from explainer import Explainer


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


# -------- LOAD YOUR PIPELINE ON SERVER START -------- #

print("Loading RAG pipeline...")

folder = os.path.join(BASE_DIR, "data", "papers")
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

print("Pipeline ready!")


# -------- API ROUTES -------- #

@app.get("/")
def home():
    return {"message": "XAI RAG API running"}


@app.post("/ask")
def ask_question(query: Query):
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
            "score": float(r["score"])
        }
        for r in results[:3]
    ]
    traces.append({
        "step": 3,
        "title": "Top Chunks Selected",
        "detail": "\n".join([
            f"Chunk {i+1}: {c['source']} | score: {c['score']:.4f} | preview: {c['text'][:80]}..."
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