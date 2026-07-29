from collections import defaultdict
from datetime import datetime
import time

from app.core.config import settings
from app.datasets.models import Dataset
from app.datasets.validator import DatasetValidator
from app.evaluation.engine import EvaluationEngine
from app.evaluation.models import EvaluationRequest
from app.experiments.models import BenchmarkResult


class BenchmarkRunner:
    """
    Executes an entire benchmark dataset using the EvaluationEngine.
    """

    def __init__(self) -> None:
        self.engine = EvaluationEngine()

    def run(
        self,
        dataset: Dataset,
    ) -> BenchmarkResult:

        DatasetValidator.validate(dataset)

        started_at = datetime.utcnow()
        start_timer = time.perf_counter()

        metric_totals: dict[str, float] = defaultdict(float)
        metric_counts: dict[str, int] = defaultdict(int)

        successful = 0
        failed = 0

        benchmark = BenchmarkResult(
            dataset_name=dataset.name,
            total_samples=len(dataset),
            started_at=started_at,
            metadata={
                "provider": settings.LLM_PROVIDER,
                "model": settings.GEMINI_MODEL,
                "engine": "EvaluationEngine",
            },
        )

        batch_size = settings.LLM_BATCH_SIZE

        for batch_start in range(
            0,
            len(dataset.samples),
            batch_size,
        ):

            batch_samples = dataset.samples[batch_start : batch_start + batch_size]

            # print(
            #     f"Processing batch {batch_start // batch_size + 1} "
            #     f"({len(batch_samples)} samples)"
            # )

            batch_requests = []

            for sample in batch_samples:

                batch_requests.append(
                    EvaluationRequest(
                        query=sample.question,
                        contexts=sample.contexts,
                        answer=sample.answer,
                        ground_truth=sample.ground_truth,
                        relevant_contexts=sample.relevant_contexts,
                    )
                )

            try:

                summaries = self.engine.evaluate_batch(batch_requests)

                for sample, summary in zip(
                    batch_samples,
                    summaries,
                ):

                    benchmark.add_result(summary)

                    successful += 1

                    for evaluator in summary.evaluators:

                        for metric in evaluator.metrics:

                            metric_totals[metric.name] += metric.score
                            metric_counts[metric.name] += 1

            except Exception as exc:

                failed += len(batch_samples)

                for offset, sample in enumerate(batch_samples):

                    benchmark.add_error(
                        sample=batch_start + offset + 1,
                        question=sample.question,
                        error=str(exc),
                    )

        average_scores = {
            metric_name: round(
                metric_totals[metric_name] / metric_counts[metric_name],
                4,
            )
            for metric_name in metric_totals
        }

        benchmark.successful_samples = successful
        benchmark.failed_samples = failed
        benchmark.completed_at = datetime.utcnow()

        benchmark.duration_ms = round(
            (time.perf_counter() - start_timer) * 1000,
            2,
        )

        benchmark.average_scores = average_scores

        return benchmark
