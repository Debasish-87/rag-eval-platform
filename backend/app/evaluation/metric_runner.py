from app.evaluation.models import (
    EvaluationRequest,
    MetricResult,
)
from app.metrics.base import BaseMetric


class MetricRunner:
    """
    Executes a collection of metrics for an evaluation request.
    """

    def __init__(
        self,
        metrics: dict[str, BaseMetric],
    ) -> None:
        self.metrics = metrics

    def run(
        self,
        request: EvaluationRequest,
    ) -> list[MetricResult]:
        """
        Compute all configured metrics and return
        them as typed MetricResult objects.
        """

        results: list[MetricResult] = []

        for name, metric in self.metrics.items():
            results.append(
                MetricResult(
                    name=name,
                    score=metric.compute(request),
                )
            )

        return results
