from app.experiments.models import (
    BenchmarkResult,
    Experiment,
)


class ExperimentManager:
    """
    Manages benchmark executions for a single experiment.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
    ) -> None:

        self.experiment = Experiment(
            name=name,
            description=description,
        )

        self.results: list[BenchmarkResult] = []

    def add_result(
        self,
        result: BenchmarkResult,
    ) -> None:
        """
        Add a benchmark result to the experiment.
        """

        self.results.append(result)

        self.experiment.benchmarks.append(result.benchmark_id)

    def get_results(
        self,
    ) -> list[BenchmarkResult]:
        """
        Return all benchmark results.
        """

        return self.results

    def latest_result(
        self,
    ) -> BenchmarkResult | None:
        """
        Return the most recent benchmark result.
        """

        if not self.results:
            return None

        return self.results[-1]

    @property
    def benchmark_count(self) -> int:
        """
        Number of benchmark runs.
        """

        return len(self.results)
