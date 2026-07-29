from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class EvaluationRequest:
    """
    Input required for evaluating a single RAG response.
    """

    query: str
    contexts: list[str]
    answer: str

    ground_truth: str | None = None

    relevant_contexts: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MetricResult:
    """
    Represents a single metric score.
    """

    name: str
    score: float


@dataclass(slots=True)
class EvaluatorResult:
    """
    Result produced by one evaluator
    (Retrieval, Generation, LLM Judge).
    """

    evaluator: str

    metrics: list[MetricResult] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)

    def metric_dict(self) -> dict[str, float]:
        """
        Convenience helper for reports.
        """

        return {metric.name: metric.score for metric in self.metrics}


@dataclass(slots=True)
class EvaluationSummary:
    """
    Complete evaluation for one sample.
    """

    evaluators: list[EvaluatorResult] = field(default_factory=list)

    def get(
        self,
        evaluator: str,
    ) -> EvaluatorResult | None:

        for item in self.evaluators:
            if item.evaluator == evaluator:
                return item

        return None
