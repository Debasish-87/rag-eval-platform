from app.evaluation.evaluator import BaseEvaluator
from app.evaluation.metric_runner import MetricRunner
from app.evaluation.models import (
    EvaluationRequest,
    EvaluatorResult,
)

from app.metrics.hit_rate import HitRate
from app.metrics.map import MAP
from app.metrics.mrr import MRR
from app.metrics.ndcg import NDCG
from app.metrics.precision import PrecisionAtK
from app.metrics.recall import RecallAtK


class RetrievalEvaluator(BaseEvaluator):
    """
    Evaluates retrieval quality using retrieval metrics.
    """

    def __init__(self) -> None:

        k = 2

        self.metric_runner = MetricRunner(
            metrics={
                f"precision@{k}": PrecisionAtK(k=k),
                f"recall@{k}": RecallAtK(k=k),
                "mrr": MRR(),
                "hit_rate": HitRate(),
                f"ndcg@{k}": NDCG(k=k),
                f"map@{k}": MAP(k=k),
            }
        )

    def evaluate(
        self,
        request: EvaluationRequest,
    ) -> EvaluatorResult:
        """
        Evaluate retrieval performance and return
        typed evaluation results.
        """

        metrics = self.metric_runner.run(request)

        return EvaluatorResult(
            evaluator="RetrievalEvaluator",
            metrics=metrics,
            metadata={
                "query": request.query,
                "retrieved_documents": len(request.contexts),
                "relevant_documents": len(request.relevant_contexts),
            },
        )
