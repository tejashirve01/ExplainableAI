import fitz
import os
from chunker import chunk_text
from embedder import Embedder
from vector_store import VectorStore
from search_engine import SearchEngine
from answer_generator import AnswerGenerator
from explainer import Explainer
from sentence_explainer import SentenceExplainer


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_pages_from_pdf(pdf_path):
    """Returns list of (page_num, text) tuples — one per page."""
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text().strip()
        if text:
            pages.append((page_num, text))
    return pages


def load_all_papers(folder):
    all_chunks = []

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)

            # Process page by page to track page numbers
            pages = extract_pages_from_pdf(path)

            for page_num, page_text in pages:
                chunks = chunk_text(page_text)

                for chunk in chunks:
                    all_chunks.append({
                        "paper": file,
                        "source": file,       # for api.py compatibility
                        "chunk": chunk,
                        "page": page_num
                    })

    return all_chunks


if __name__ == "__main__":

    folder = "../data/papers"

    chunks = load_all_papers(folder)

    print("Total Chunks:", len(chunks))

    texts = [c["chunk"] for c in chunks]

    embedder = Embedder()
    embeddings = embedder.embed(texts)

    dimension = embeddings.shape[1]
    vector_db = VectorStore(dimension)
    vector_db.add_embeddings(embeddings)

    print("Vector database ready!")

    search_engine = SearchEngine(embedder, vector_db, chunks)

    query = input("\nAsk a question: ")

    results = search_engine.search(query)

    print("\nTop Results:\n")

    for r in results:
        print("Paper:", r["paper"])
        print("Page:", r["page"])                        # ← now shows page
        print("Similarity Score:", round(r["score"], 3))
        print("Evidence:", r["chunk"][:250])
        print("\n--------------------\n")

    generator = AnswerGenerator()
    answer = generator.generate(query, results)

    scores = [r["score"] for r in results]
    confidence = sum(scores) / len(scores)

    print("\nFinal Answer:\n")
    print(answer)
    print("\nConfidence Score:", round(confidence * 100, 2), "%")

    explainer = Explainer()
    keywords = explainer.extract_keywords(results)

    print("\nImportant Keywords:")
    for k in keywords:
        print("-", k)

    sentence_explainer = SentenceExplainer()
    sentence = sentence_explainer.extract_sentence(results, query)

    print("\nEvidence Sentence:")
    print(sentence)