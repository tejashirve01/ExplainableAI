from sentence_transformers import SentenceTransformer
import os

class Embedder:
    def __init__(self):
        print("Loading embedding model...")
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(base_dir, "models", "all-MiniLM-L6-v2")
        self.model = SentenceTransformer(model_path)
        print("Model loaded!")

    def embed(self, texts):
        return self.model.encode(texts)