from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class HitRate(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        for document in request.contexts:
            if document in request.relevant_contexts:
                return 1.0

        return 0.0
