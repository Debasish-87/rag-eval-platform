from app.evaluation.models import EvaluationRequest
from app.metrics.base import BaseMetric


class Correctness(BaseMetric):

    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:

        if not request.ground_truth:
            return 0.0

        answer = request.answer.strip().lower()
        ground_truth = request.ground_truth.strip().lower()

        if answer == ground_truth:
            return 1.0

        return 0.0
