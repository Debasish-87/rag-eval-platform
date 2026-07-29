from app.evaluation.models import (
    EvaluationRequest,
    EvaluationSummary,
)
from app.evaluation.registry import EvaluatorRegistry


class EvaluationEngine:
    """
    Executes all registered evaluators.
    """

    def __init__(self) -> None:
        self.evaluators = EvaluatorRegistry.get_evaluators()

    def evaluate(
        self,
        request: EvaluationRequest,
    ) -> EvaluationSummary:
        """
        Run all evaluators for a single request.
        """

        summary = EvaluationSummary()

        for evaluator in self.evaluators:
            result = evaluator.evaluate(request)
            summary.evaluators.append(result)

        return summary

    def evaluate_batch(
        self,
        requests: list[EvaluationRequest],
    ) -> list[EvaluationSummary]:
        """
        Run all evaluators for multiple requests.
        """

        summaries = [EvaluationSummary() for _ in requests]

        for evaluator in self.evaluators:

            results = evaluator.evaluate_batch(requests)

            if len(results) != len(requests):
                raise ValueError(
                    f"{evaluator.__class__.__name__} returned "
                    f"{len(results)} results for "
                    f"{len(requests)} requests."
                )

            for summary, result in zip(
                summaries,
                results,
            ):
                summary.evaluators.append(result)

        return summaries
