class SearchEngine:

    def __init__(self, embedder, vector_store, chunks):

        self.embedder = embedder
        self.vector_store = vector_store
        self.chunks = chunks

    def search(self, query, k=3):

        query_embedding = self.embedder.embed([query])[0]

        distances, indices = self.vector_store.search(query_embedding, k)

        results = []

        for i, idx in enumerate(indices[0]):

            score = 1 / (1 + distances[0][i])

            chunk = self.chunks[idx]

            results.append({
                "paper":  chunk.get("paper", "unknown"),
                "source": chunk.get("source", chunk.get("paper", "unknown")),
                "page":   chunk.get("page", "unknown"),
                "chunk":  chunk["chunk"],
                "score":  score
            })

        return results