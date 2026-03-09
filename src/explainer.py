from sklearn.feature_extraction.text import TfidfVectorizer


class Explainer:

    def extract_keywords(self, results, top_k=5):

        texts = [r["chunk"] for r in results]

        vectorizer = TfidfVectorizer(stop_words="english")

        X = vectorizer.fit_transform(texts)

        scores = X.sum(axis=0).A1

        words = vectorizer.get_feature_names_out()

        word_scores = list(zip(words, scores))

        word_scores.sort(key=lambda x: x[1], reverse=True)

        keywords = [w[0] for w in word_scores[:top_k]]

        return keywords