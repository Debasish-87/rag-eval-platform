from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class MRR(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        for rank, document in enumerate(
            request.contexts,
            start=1,
        ):
            if document in request.relevant_contexts:
                return 1 / rank

        return 0.0
