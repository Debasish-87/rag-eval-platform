from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class PrecisionAtK(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        k = self.config.get("k", len(request.contexts))

        retrieved = request.contexts[:k]
        relevant = request.relevant_contexts

        if not retrieved:
            return 0.0

        hits = sum(1 for document in retrieved if document in relevant)

        return hits / len(retrieved)
