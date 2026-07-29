from abc import ABC, abstractmethod

from app.evaluation.models import (
    EvaluationRequest,
    EvaluatorResult,
)


class BaseEvaluator(ABC):
    """
    Base interface for all evaluation components.
    """

    @abstractmethod
    def evaluate(
        self,
        request: EvaluationRequest,
    ) -> EvaluatorResult:
        """
        Evaluate a single request and return the evaluator result.
        """
        raise NotImplementedError

    def evaluate_batch(
        self,
        requests: list[EvaluationRequest],
    ) -> list[EvaluatorResult]:
        """
        Default batch implementation.

        Evaluators that support native batching can override this
        method for better performance.
        """
        return [self.evaluate(request) for request in requests]
