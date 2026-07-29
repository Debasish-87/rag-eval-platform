from app.evaluation.evaluator import BaseEvaluator
from app.evaluation.metric_runner import MetricRunner
from app.evaluation.models import (
    EvaluationRequest,
    EvaluatorResult,
)

from app.metrics.correctness import Correctness
from app.metrics.faithfulness import Faithfulness
from app.metrics.semantic_similarity import SemanticSimilarity


class GenerationEvaluator(BaseEvaluator):
    """
    Evaluates the quality of a generated answer using
    generation-based metrics.
    """

    def __init__(self) -> None:
        self.metric_runner = MetricRunner(
            metrics={
                "faithfulness": Faithfulness(),
                "correctness": Correctness(),
                "semantic_similarity": SemanticSimilarity(),
            }
        )

    def evaluate(
        self,
        request: EvaluationRequest,
    ) -> EvaluatorResult:
        """
        Evaluate the generated answer and return
        typed evaluation results.
        """

        metrics = self.metric_runner.run(request)

        return EvaluatorResult(
            evaluator="GenerationEvaluator",
            metrics=metrics,
            metadata={
                "answer_length": len(request.answer),
                "contexts_used": len(request.contexts),
            },
        )
