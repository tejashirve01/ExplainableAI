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
from sentence_explainer import SentenceExplainer


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

sentence_explainer = SentenceExplainer()

print("Pipeline ready!")


# -------- API ROUTES -------- #

@app.get("/")
def home():
    return {"message": "XAI RAG API running"}


@app.post("/ask")
def ask_question(query: Query):

    question = query.question

    results = search_engine.search(question)

    answer = generator.generate(question, results)

    scores = [r["score"] for r in results]
    confidence = sum(scores) / len(scores)

    keywords = explainer.extract_keywords(results)

    sentence = sentence_explainer.extract_sentence(results, question)

    return {
        "answer": answer,
        "confidence": float(confidence),
        "evidence_chunk": results[0]["chunk"],
        "evidence_sentence": sentence,
        "keywords": keywords
    }
