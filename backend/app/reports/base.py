from abc import ABC, abstractmethod
from pathlib import Path

from app.experiments.models import BenchmarkResult


class BaseReport(ABC):
    """
    Abstract base class for benchmark report generators.
    """

    @abstractmethod
    def generate(
        self,
        result: BenchmarkResult,
        output_path: str | Path,
    ) -> None:
        """
        Generate a report for a benchmark result.

        Args:
            result: Benchmark execution result.
            output_path: Destination file path.
        """
        raise NotImplementedError
