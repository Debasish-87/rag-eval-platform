import re

from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


class SemanticSimilarity(BaseMetric):
    """
    Cosine similarity between the answer and ground truth embeddings.

    Loads a sentence-transformers model lazily on first use. If the
    model can't be loaded (no internet access, dependency not
    installed, etc.) this degrades gracefully to a Jaccard
    token-overlap similarity, so the evaluation pipeline still runs
    end to end in offline / demo environments.
    """

    _model = None
    _model_load_failed = False

    def __init__(self, **config):
        super().__init__(**config)
        self.model_name = config.get("model_name", "all-MiniLM-L6-v2")

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        if not request.ground_truth:
            return 0.0

        model = self._get_model(self.model_name)

        if model is not None:
            try:
                from sentence_transformers.util import cos_sim

                answer_embedding = model.encode(
                    request.answer,
                    convert_to_tensor=True,
                )

                truth_embedding = model.encode(
                    request.ground_truth,
                    convert_to_tensor=True,
                )

                similarity = cos_sim(
                    answer_embedding,
                    truth_embedding,
                )

                return round(float(similarity.item()), 4)

            except Exception:
                # Fall through to the lexical fallback below.
                pass

        return self._lexical_similarity(
            request.answer,
            request.ground_truth,
        )

    @classmethod
    def _get_model(cls, model_name: str):
        if cls._model is not None:
            return cls._model

        if cls._model_load_failed:
            return None

        try:
            from sentence_transformers import SentenceTransformer

            cls._model = SentenceTransformer(model_name)

            return cls._model

        except Exception:
            cls._model_load_failed = True
            return None

    @staticmethod
    def _lexical_similarity(answer: str, ground_truth: str) -> float:
        answer_tokens = _tokenize(answer)
        truth_tokens = _tokenize(ground_truth)

        if not answer_tokens or not truth_tokens:
            return 0.0

        intersection = len(answer_tokens & truth_tokens)
        union = len(answer_tokens | truth_tokens)

        return round(intersection / union, 4) if union else 0.0
