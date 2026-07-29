from math import log2

from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class NDCG(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        k = self.config.get("k", len(request.contexts))

        retrieved = request.contexts[:k]
        relevant = request.relevant_contexts

        if not retrieved or not relevant:
            return 0.0

        # DCG Calculate for nDCG
        dcg = 0.0

        for rank, document in enumerate(retrieved, start=1):
            if document in relevant:
                dcg += 1 / log2(rank + 1)

        ideal_hits = min(len(relevant), k)
        # Ideal DCG for nDCG
        idcg = sum(1 / log2(rank + 1) for rank in range(1, ideal_hits + 1))

        if idcg == 0:
            return 0.0

        return dcg / idcg
