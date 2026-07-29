import csv
from pathlib import Path

from app.experiments.models import BenchmarkResult
from app.reports.base import BaseReport


class CSVReport(BaseReport):
    """
    Export per-sample benchmark results as CSV.
    """

    def generate(
        self,
        result: BenchmarkResult,
        output_path: str | Path,
    ) -> None:

        output_path = Path(output_path)

        rows: list[dict[str, float]] = []

        for summary in result.results:

            row: dict[str, float] = {}

            for evaluator in summary.evaluators:

                for metric in evaluator.metrics:

                    row[metric.name] = metric.score

            rows.append(row)

        if not rows:
            return

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        fieldnames = sorted({key for row in rows for key in row.keys()})

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(rows)
