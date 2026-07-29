from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.evaluation.models import EvaluationSummary


@dataclass(slots=True)
class Experiment:
    """
    Lightweight, in-memory record of an experiment (a named,
    ongoing series of benchmark runs against one RAG system).
    """

    name: str
    description: str = ""

    experiment_id: str = field(default_factory=lambda: str(uuid4()))

    created_at: datetime = field(default_factory=datetime.utcnow)

    # Benchmark IDs produced by this experiment.
    benchmarks: list[str] = field(default_factory=list)


@dataclass(slots=True)
class BenchmarkError:
    """
    Represents a failed benchmark sample.
    """

    sample: int
    question: str
    error: str


@dataclass(slots=True)
class BenchmarkResult:
    """
    Represents the outcome of a benchmark execution.
    """

    # Unique benchmark identifier
    benchmark_id: str = field(default_factory=lambda: str(uuid4()))

    # Dataset information
    dataset_name: str = ""
    dataset_version: str = "1.0"

    # Execution statistics
    total_samples: int = 0
    successful_samples: int = 0
    failed_samples: int = 0

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None
    duration_ms: float = 0.0

    # Aggregated metrics
    average_scores: dict[str, float] = field(default_factory=dict)

    # Per-sample evaluation results
    results: list[EvaluationSummary] = field(default_factory=list)

    # Failed evaluations
    errors: list[BenchmarkError] = field(default_factory=list)

    # Runtime information
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """
        Percentage of successfully evaluated samples.
        """

        if self.total_samples == 0:
            return 0.0

        return round(
            self.successful_samples / self.total_samples,
            4,
        )

    @property
    def failure_rate(self) -> float:
        """
        Percentage of failed samples.
        """

        if self.total_samples == 0:
            return 0.0

        return round(
            self.failed_samples / self.total_samples,
            4,
        )

    @property
    def is_successful(self) -> bool:
        """
        True if all samples were evaluated successfully.
        """

        return self.failed_samples == 0

    def add_result(
        self,
        result: EvaluationSummary,
    ) -> None:
        """
        Add a single sample evaluation.
        """

        self.results.append(result)

    def add_error(
        self,
        *,
        sample: int,
        question: str,
        error: str,
    ) -> None:
        """
        Add a failed sample.
        """

        self.errors.append(
            BenchmarkError(
                sample=sample,
                question=question,
                error=error,
            )
        )
