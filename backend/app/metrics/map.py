from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class MAP(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        k = self.config.get("k", len(request.contexts))

        retrieved = request.contexts[:k]
        relevant = set(request.relevant_contexts)

        if not retrieved or not relevant:
            return 0.0

        hits = 0
        precision_sum = 0.0

        for rank, document in enumerate(retrieved, start=1):
            if document in relevant:
                hits += 1
                precision_sum += hits / rank

        if hits == 0:
            return 0.0

        return precision_sum / min(len(relevant), k)
