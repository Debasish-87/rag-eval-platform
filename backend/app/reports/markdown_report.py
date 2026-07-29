from pathlib import Path

from app.experiments.models import BenchmarkResult
from app.reports.base import BaseReport


class MarkdownReport(BaseReport):
    """
    Export benchmark results as a Markdown report.
    """

    def generate(
        self,
        result: BenchmarkResult,
        output_path: str | Path,
    ) -> None:

        output_path = Path(output_path)

        lines: list[str] = []

        lines.append("# Benchmark Report\n\n")

        lines.append(f"**Benchmark ID:** {result.benchmark_id}\n\n")

        lines.append(f"**Dataset:** {result.dataset_name}\n\n")

        lines.append(f"**Dataset Version:** {result.dataset_version}\n\n")

        lines.append(f"**Duration:** {result.duration_ms:.2f} ms\n\n")

        lines.append(f"**Total Samples:** {result.total_samples}\n\n")

        lines.append(f"**Successful:** {result.successful_samples}\n\n")

        lines.append(f"**Failed:** {result.failed_samples}\n\n")

        lines.append(f"**Success Rate:** {result.success_rate:.2%}\n\n")

        lines.append(f"**Failure Rate:** {result.failure_rate:.2%}\n\n")

        lines.append("## Average Scores\n\n")

        if result.average_scores:

            lines.append("| Metric | Score |\n")
            lines.append("|--------|------:|\n")

            for metric, score in sorted(result.average_scores.items()):
                lines.append(f"| {metric} | {score:.4f} |\n")

        else:
            lines.append("_No evaluation metrics available._\n")

        if result.errors:

            lines.append("\n## Errors\n\n")

            for error in result.errors:
                lines.append(
                    f"- Sample {error.sample}: "
                    f"{error.question} "
                    f"({error.error})\n"
                )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            "".join(lines),
            encoding="utf-8",
        )
