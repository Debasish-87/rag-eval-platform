import json
from dataclasses import asdict
from pathlib import Path

from app.experiments.models import BenchmarkResult
from app.reports.base import BaseReport


class JSONReport(BaseReport):
    """
    Export a benchmark result as JSON.
    """

    def generate(
        self,
        result: BenchmarkResult,
        output_path: str | Path,
    ) -> None:

        output_path = Path(output_path)

        data = asdict(result)

        data["started_at"] = (
            result.started_at.isoformat() if result.started_at else None
        )

        data["completed_at"] = (
            result.completed_at.isoformat() if result.completed_at else None
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )
