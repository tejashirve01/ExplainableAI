from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")

sys.path.append(SRC_PATH)

# Import your backend modules
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
    question = query.question
    results = search_engine.search(question)

    result = generator.generate_with_reasoning(question, results)
    answer = result["answer"]

    if "cannot find the answer" in answer.lower():
        return {
            "answer": answer,
            "confidence": 0.0,
            "reasoning": "No relevant chunks found in the documents.",
            "keywords": None,
            "chunks": []
        }

    scores = [float(r["score"]) for r in results]
    numeric_confidence = round(sum(scores) / len(scores), 4)
    keywords = explainer.extract_keywords(results)

    # Include top 3 chunks in response
    top_chunks = [
        {
            "text": r["chunk"],
            "source": r.get("source", "unknown"),
            "score": float(r["score"])
        }
        for r in results[:3]
    ]

    return {
        "answer": answer,
        "confidence": float(numeric_confidence),
        "confidence_level": result["confidence_level"],
        "reasoning": result["reasoning"],
        "keywords": keywords,
        "chunks": top_chunks
    }