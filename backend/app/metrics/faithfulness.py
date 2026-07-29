import re

from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric

_STOPWORDS = {
    "a",
    "an",
    "the",
    "is",
    "was",
    "are",
    "were",
    "be",
    "been",
    "being",
    "of",
    "in",
    "on",
    "at",
    "to",
    "for",
    "and",
    "or",
    "as",
    "by",
    "with",
    "it",
    "its",
    "this",
    "that",
    "these",
    "those",
    "also",
    "part",
    "official",
}


def _content_tokens(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    return {token for token in tokens if token not in _STOPWORDS}


class Faithfulness(BaseMetric):
    """
    Graded faithfulness score: the fraction of the answer's content
    words that are grounded in the retrieved context. 1.0 means every
    claim word in the answer is backed by the context; lower scores
    indicate potentially unsupported (hallucinated) content.
    """

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        answer_tokens = _content_tokens(request.answer)

        if not answer_tokens:
            return 0.0

        context_tokens = _content_tokens(" ".join(request.contexts))

        if not context_tokens:
            return 0.0

        supported = len(answer_tokens & context_tokens)

        return round(supported / len(answer_tokens), 4)
