import json
import re

from app.llm.base import BaseLLMClient


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class MockLLMClient(BaseLLMClient):
    """
    Deterministic, offline stand-in for a real LLM judge.

    Scores are derived from lexical overlap between the generated
    answer and the retrieved context / question, so the platform
    produces sensible, reproducible results without any network
    access or API key. Swap LLM_PROVIDER to "gemini" (with
    GEMINI_API_KEY set) for real LLM-as-judge scoring.
    """

    def evaluate(self, prompt: str) -> str:
        question, context, answer = self._extract_sections(prompt)

        answer_tokens = _tokenize(answer)
        context_tokens = _tokenize(context)
        question_tokens = _tokenize(question)

        faithfulness = self._overlap_ratio(
            answer_tokens,
            context_tokens,
        )

        answer_relevance = self._overlap_ratio(
            answer_tokens,
            question_tokens,
            floor=0.35,
        )

        hallucination = round(
            max(0.0, min(1.0, 1.0 - faithfulness)),
            4,
        )

        reason = (
            "Heuristic mock judge: answer shares "
            f"{round(faithfulness * 100)}% of its key terms "
            "with the retrieved context."
        )

        return json.dumps(
            {
                "faithfulness": faithfulness,
                "answer_relevance": answer_relevance,
                "hallucination": hallucination,
                "reason": reason,
            }
        )

    @staticmethod
    def _extract_sections(prompt: str) -> tuple[str, str, str]:
        question_match = re.search(r"Question:\s*(.*?)\n\n", prompt, re.DOTALL)
        context_match = re.search(r"Retrieved Context:\s*(.*?)\n\n", prompt, re.DOTALL)
        answer_match = re.search(r"Generated Answer:\s*(.*?)\n\n", prompt, re.DOTALL)

        question = question_match.group(1).strip() if question_match else ""
        context = context_match.group(1).strip() if context_match else ""
        answer = answer_match.group(1).strip() if answer_match else ""

        return question, context, answer

    @staticmethod
    def _overlap_ratio(
        answer_tokens: set[str],
        reference_tokens: set[str],
        floor: float = 0.05,
    ) -> float:
        if not answer_tokens or not reference_tokens:
            return floor

        overlap = len(answer_tokens & reference_tokens)
        ratio = overlap / len(answer_tokens)

        # Blend toward a high score for strong overlap while keeping
        # a realistic floor so scores aren't a flat 0/1 distribution.
        score = floor + (1 - floor) * ratio

        return round(max(0.0, min(1.0, score)), 4)
