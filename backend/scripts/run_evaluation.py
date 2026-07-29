#!/usr/bin/env python3
"""
End-to-end RAG evaluation pipeline.

Runs the full flow with a single command:

    python scripts/run_evaluation.py

    1. Load the benchmark dataset
    2. Run every registered evaluator (retrieval, generation, LLM judge)
    3. Persist Evaluation + Metric rows, update Benchmark status
    4. Refresh the leaderboard (computed live from the DB)
    5. Generate JSON / CSV / Markdown reports
    6. Print a production-style summary to the terminal

See `python scripts/run_evaluation.py --help` for options.
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

# Make `app` importable when run as `python scripts/run_evaluation.py`
# from the backend/ directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.datasets.exceptions import DatasetValidationError  # noqa: E402
from app.datasets.loader import DatasetLoader  # noqa: E402
from app.datasets.validator import DatasetValidator  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.database import SessionLocal, engine  # noqa: E402
from app.experiments.benchmark import BenchmarkRunner  # noqa: E402
from app.models.benchmark import Benchmark  # noqa: E402
from app.models.dataset import Dataset as DatasetModel  # noqa: E402
from app.models.evaluation import Evaluation  # noqa: E402
from app.models.experiment import Experiment  # noqa: E402
from app.models.metric import Metric  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.reports import CSVReport, JSONReport, MarkdownReport  # noqa: E402


# --------------------------------------------------------------------------
# Terminal styling
# --------------------------------------------------------------------------


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"

    @classmethod
    def enabled(cls) -> bool:
        return sys.stdout.isatty()


def c(text: str, color: str) -> str:
    if not Style.enabled():
        return text
    return f"{color}{text}{Style.RESET}"


def header(title: str) -> None:
    line = "=" * 55
    print(c(line, Style.CYAN))
    print(c(title, Style.BOLD))
    print(c(line, Style.CYAN))
    print()


def row(label: str, value: str, ok: bool | None = None) -> None:
    mark = ""
    if ok is True:
        mark = c(" \u2713", Style.GREEN)
    elif ok is False:
        mark = c(" \u2717", Style.RED)
    print(f"{label:<28}{value}{mark}")


def section(title: str) -> None:
    print()
    print(c(title, Style.MAGENTA + Style.BOLD))
    print()


def metric_row(name: str, score: float) -> None:
    bar_len = 24
    filled = max(0, min(bar_len, round(score * bar_len)))
    bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
    print(f"  {name:<22}{c(bar, Style.GREEN)}  {score:.4f}")


def progress(current: int, total: int, prefix: str = "Evaluating") -> None:
    bar_len = 30
    filled = int(bar_len * current / max(total, 1))
    bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
    pct = current / max(total, 1) * 100
    end = "\n" if current == total else "\r"
    print(
        f"{prefix:<12}[{bar}] {current}/{total} ({pct:5.1f}%)",
        end=end,
        flush=True,
    )


RETRIEVAL_METRICS = {
    "precision@2",
    "recall@2",
    "mrr",
    "map@2",
    "ndcg@2",
    "hit_rate",
}

GENERATION_METRICS = {
    "faithfulness",
    "correctness",
    "semantic_similarity",
}

JUDGE_METRICS = {
    "llm_faithfulness",
    "answer_relevance",
    "hallucination",
}


# --------------------------------------------------------------------------
# DB helpers (get-or-create)
# --------------------------------------------------------------------------


def get_or_create_project(db: Session, name: str, description: str) -> Project:
    project = db.scalar(select(Project).where(Project.name == name))

    if project is None:
        project = Project(name=name, description=description)
        db.add(project)
        db.commit()
        db.refresh(project)

    return project


def get_or_create_dataset(
    db: Session,
    project: Project,
    name: str,
    version: str,
    file_path: str,
) -> DatasetModel:
    dataset = db.scalar(
        select(DatasetModel).where(
            DatasetModel.project_id == project.id,
            DatasetModel.name == name,
            DatasetModel.version == version,
        )
    )

    if dataset is None:
        dataset = DatasetModel(
            project_id=project.id,
            name=name,
            version=version,
            file_path=file_path,
        )
        db.add(dataset)
        db.commit()
        db.refresh(dataset)

    return dataset


def get_or_create_experiment(
    db: Session,
    project: Project,
    name: str,
    description: str,
) -> Experiment:
    experiment = db.scalar(
        select(Experiment).where(
            Experiment.project_id == project.id,
            Experiment.name == name,
        )
    )

    if experiment is None:
        experiment = Experiment(
            project_id=project.id,
            name=name,
            description=description,
        )
        db.add(experiment)
        db.commit()
        db.refresh(experiment)

    return experiment


def create_benchmark(db: Session, experiment: Experiment, name: str) -> Benchmark:
    benchmark = Benchmark(
        experiment_id=experiment.id,
        name=name,
        status="running",
    )
    db.add(benchmark)
    db.commit()
    db.refresh(benchmark)
    return benchmark


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------


@dataclass
class PipelineArgs:
    dataset: str
    project: str
    experiment: str
    benchmark: str
    reports_dir: str


def parse_args(argv: list[str] | None = None) -> PipelineArgs:
    parser = argparse.ArgumentParser(
        description="Run the full RAG evaluation pipeline end to end.",
    )
    parser.add_argument(
        "--dataset",
        default="app/datasets/sample_dataset.json",
        help="Path to a benchmark dataset JSON file.",
    )
    parser.add_argument(
        "--project",
        default="RAG Evaluation Platform Demo",
        help="Project name (created if it doesn't exist).",
    )
    parser.add_argument(
        "--experiment",
        default=(
            settings.GEMINI_MODEL
            if settings.LLM_PROVIDER == "gemini"
            else "gemini-flash"
        ),
        help="Experiment / system-under-test name.",
    )
    parser.add_argument(
        "--benchmark",
        default=None,
        help="Benchmark run name (default: timestamped).",
    )
    parser.add_argument(
        "--reports-dir",
        default=settings.REPORTS_DIR,
        help="Directory to write JSON/CSV/Markdown reports to.",
    )

    args = parser.parse_args(argv)

    benchmark_name = args.benchmark or (
        f"benchmark-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    )

    return PipelineArgs(
        dataset=args.dataset,
        project=args.project,
        experiment=args.experiment,
        benchmark=benchmark_name,
        reports_dir=args.reports_dir,
    )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    header("RAG Evaluation Platform")

    # ---------------------------------------------------------------
    # 0. Ensure tables exist (works with SQLite out of the box; a
    #    no-op if Alembic has already created the schema, e.g. on
    #    Postgres).
    # ---------------------------------------------------------------
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # -------------------------------------------------------
        # 1. Load + validate dataset
        # -------------------------------------------------------
        dataset_path = Path(args.dataset)

        try:
            dataset = DatasetLoader.load(dataset_path)
            DatasetValidator.validate(dataset)
        except (FileNotFoundError, ValueError, DatasetValidationError) as exc:
            row("Dataset Loaded", str(exc), ok=False)
            return 1

        row("Dataset Loaded", "", ok=True)
        row("Questions", str(len(dataset)))
        print()

        # -------------------------------------------------------
        # 2. Register project / dataset / experiment / benchmark
        # -------------------------------------------------------
        project = get_or_create_project(
            db,
            args.project,
            "Automatically created by run_evaluation.py",
        )

        get_or_create_dataset(
            db,
            project,
            dataset.name,
            version="1.0",
            file_path=str(dataset_path),
        )

        experiment = get_or_create_experiment(
            db,
            project,
            args.experiment,
            f"LLM provider: {settings.LLM_PROVIDER}",
        )

        benchmark = create_benchmark(db, experiment, args.benchmark)

        # -------------------------------------------------------
        # 3. Run the evaluation engine over every sample
        # -------------------------------------------------------
        runner = BenchmarkRunner()

        total = len(dataset)
        progress(0, total)

        start = time.perf_counter()
        result = runner.run(dataset)
        for i in range(1, total + 1):
            progress(i, total)
        duration = time.perf_counter() - start

        # -------------------------------------------------------
        # 4. Persist Evaluation + Metric rows
        # -------------------------------------------------------
        for sample, summary in zip(dataset.samples, result.results):
            evaluation = Evaluation(
                benchmark_id=benchmark.id,
                query=sample.question,
                answer=sample.answer,
                ground_truth=sample.ground_truth,
            )
            db.add(evaluation)
            db.flush()  # get evaluation.id without a full commit

            for evaluator_result in summary.evaluators:
                for metric in evaluator_result.metrics:
                    db.add(
                        Metric(
                            evaluation_id=evaluation.id,
                            name=metric.name,
                            score=metric.score,
                        )
                    )

        benchmark.status = "completed"
        benchmark.completed_at = datetime.now(timezone.utc)
        db.commit()

        # -------------------------------------------------------
        # 5. Print grouped metric summaries
        # -------------------------------------------------------
        section("Running Retrieval Metrics...")
        for name, score in sorted(result.average_scores.items()):
            if name in RETRIEVAL_METRICS:
                metric_row(name, score)

        section("Running Generation Metrics...")
        for name, score in sorted(result.average_scores.items()):
            if name in GENERATION_METRICS:
                metric_row(name, score)

        judge_only = JUDGE_METRICS - GENERATION_METRICS
        judge_present = {
            name: score
            for name, score in result.average_scores.items()
            if name in judge_only
        }
        if judge_present:
            section("Running LLM-Judge Metrics...")
            for name, score in sorted(judge_present.items()):
                metric_row(name, score)

        # -------------------------------------------------------
        # 6. Generate reports
        # -------------------------------------------------------
        section("Saving Results...")

        reports_dir = Path(args.reports_dir)

        json_path = reports_dir / f"benchmark_{benchmark.id}.json"
        csv_path = reports_dir / f"benchmark_{benchmark.id}.csv"
        md_path = reports_dir / f"benchmark_{benchmark.id}.md"

        result.benchmark_id = str(benchmark.id)

        JSONReport().generate(result, json_path)
        CSVReport().generate(result, csv_path)
        MarkdownReport().generate(result, md_path)

        # Also write the "latest run" under stable, predictable names.
        JSONReport().generate(result, reports_dir / "report.json")
        CSVReport().generate(result, reports_dir / "report.csv")
        MarkdownReport().generate(result, reports_dir / "report.md")

        row("Leaderboard Updated", "", ok=True)
        row("Reports Generated", "", ok=True)

        # -------------------------------------------------------
        # 7. Final summary
        # -------------------------------------------------------
        overall_score = (
            round(
                sum(result.average_scores.values()) / len(result.average_scores),
                4,
            )
            if result.average_scores
            else 0.0
        )

        header("Evaluation Completed")

        row("Benchmark", f"#{benchmark.id} ({benchmark.name})")
        row("Experiment", experiment.name)
        row("Duration", f"{duration:.2f}s")
        row(
            "Successful / Failed",
            f"{result.successful_samples} / {result.failed_samples}",
        )
        row("Overall Average Score", f"{overall_score:.4f}")
        print()
        row("JSON Report", str(json_path))
        row("CSV Report", str(csv_path))
        row("Markdown Report", str(md_path))
        print()
        print(c("API docs:      http://localhost:8000/docs", Style.DIM))
        print(c("Dashboard:     http://localhost:5500", Style.DIM))
        print()

        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
