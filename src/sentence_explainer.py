import re


class SentenceExplainer:

    def extract_sentence(self, results, query):

        sentences = []

        for r in results:

            text = r["chunk"]

            split_sentences = re.split(r'[.!?]', text)

            for s in split_sentences:

                if query.lower() in s.lower():

                    return s.strip()

            sentences.extend(split_sentences)

        return sentences[0].strip()