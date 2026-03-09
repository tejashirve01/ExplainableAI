from transformers import pipeline


class AnswerGenerator:

    def __init__(self):

        print("Loading LLM...")

        self.generator = pipeline(
            "text-generation",
            model="gpt2"
        )

        print("LLM Loaded!")


    def generate(self, question, contexts):

        context_text = ""

        for c in contexts:
            context_text += c["chunk"][:200] + "\n"

        prompt = f"""
                Context:
                {context_text}

                Question: {question}

                Answer:
"""

        result = self.generator(
            prompt,
            max_length=80,
            do_sample=False
        )

        return result[0]["generated_text"]