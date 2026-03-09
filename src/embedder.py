from sentence_transformers import SentenceTransformer


class Embedder:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        print("Model loaded!")

    def embed(self, texts):

        embeddings = self.model.encode(texts)

        return embeddings