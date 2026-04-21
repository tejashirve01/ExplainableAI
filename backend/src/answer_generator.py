from google import genai
import os
from dotenv import load_dotenv


class AnswerGenerator:

    def __init__(self):
        print("Loading Gemini LLM...")
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        print("Gemini Loaded!")

    def generate(self, question, results):
        context = "\n".join([r["chunk"] for r in results])

        prompt = f"""
You are an expert research assistant.

Use ONLY the provided context to answer the question.

If the answer is not in the context say:
"I cannot find the answer in the documents."

Context:
{context}

Question:
{question}

Explain the answer clearly.
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text

    def generate_with_reasoning(self, question, results):

        context = "\n\n".join([
            f"[Chunk {i+1} | Source: {r.get('source', 'unknown')} | Score: {r['score']:.3f}]\n{r['chunk']}"
            for i, r in enumerate(results)
        ])

        prompt = f"""
You are an expert research assistant.

Use ONLY the provided context chunks to answer the question.
Each chunk is labeled with its source and relevance score.

If the answer is not in the context, say:
"I cannot find the answer in the documents."

Context:
{context}

Question:
{question}

Respond in EXACTLY this format (do not add extra sections):

ANSWER:
<your detailed answer here>

REASONING:
<explain step by step:
 - which chunks were most relevant and why
 - what specific information from those chunks supports the answer
 - any limitations or gaps in the retrieved context>

CONFIDENCE:
<one of: high / medium / low>
<one sentence explaining why>
"""

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return self._parse_response(response.text, results)

    def _parse_response(self, raw: str, results: list) -> dict:

        answer, reasoning, confidence_level, confidence_reason = "", "", "medium", ""

        current_section = None

        for line in raw.splitlines():
            stripped = line.strip()

            if stripped == "ANSWER:":
                current_section = "answer"
            elif stripped == "REASONING:":
                current_section = "reasoning"
            elif stripped == "CONFIDENCE:":
                current_section = "confidence"
            elif current_section == "answer":
                answer += line + "\n"
            elif current_section == "reasoning":
                reasoning += line + "\n"
            elif current_section == "confidence":
                lower = stripped.lower()
                if lower in ("high", "medium", "low"):
                    confidence_level = lower
                elif stripped:
                    confidence_reason = stripped

        # Append source summary to reasoning
        sources_summary = "\n".join([
            f"  - Chunk {i+1}: {r.get('source', 'unknown')} (score: {r['score']:.3f})"
            for i, r in enumerate(results)
        ])

        full_reasoning = (
            reasoning.strip()
            + f"\n\nRetrieved chunks used:\n{sources_summary}"
        )

        if confidence_reason:
            full_reasoning += f"\n\nConfidence note: {confidence_reason}"

        return {
            "answer": answer.strip(),
            "reasoning": full_reasoning.strip(),
            "confidence_level": confidence_level
        }