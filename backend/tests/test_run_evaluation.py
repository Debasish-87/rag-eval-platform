import importlib.util
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = BACKEND_DIR / "scripts" / "run_evaluation.py"


def _load_run_evaluation_module():
    """
    Import scripts/run_evaluation.py as a module without needing
    scripts/ to be a package.
    """

    spec = importlib.util.spec_from_file_location("run_evaluation_script", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pipeline_runs_end_to_end(tmp_path, sample_dataset_path, capsys):
    run_evaluation = _load_run_evaluation_module()

    reports_dir = tmp_path / "reports"

    exit_code = run_evaluation.main(
        [
            "--dataset",
            sample_dataset_path,
            "--project",
            "Integration Test Project",
            "--experiment",
            "integration-test-experiment",
            "--benchmark",
            "integration-test-benchmark",
            "--reports-dir",
            str(reports_dir),
        ]
    )

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Evaluation Completed" in captured.out
    assert "Dataset Loaded" in captured.out

    # Reports were written to disk.
    json_reports = list(reports_dir.glob("benchmark_*.json"))
    csv_reports = list(reports_dir.glob("benchmark_*.csv"))
    md_reports = list(reports_dir.glob("benchmark_*.md"))

    assert json_reports, "expected a benchmark_<id>.json report"
    assert csv_reports, "expected a benchmark_<id>.csv report"
    assert md_reports, "expected a benchmark_<id>.md report"

    assert (reports_dir / "report.json").exists()
    assert (reports_dir / "report.csv").exists()
    assert (reports_dir / "report.md").exists()


def test_pipeline_persists_evaluations_and_completes_benchmark(
    tmp_path, sample_dataset_path, db_session
):
    from sqlalchemy import select

    from app.models.benchmark import Benchmark
    from app.models.evaluation import Evaluation
    from app.models.experiment import Experiment

    run_evaluation = _load_run_evaluation_module()

    run_evaluation.main(
        [
            "--dataset",
            sample_dataset_path,
            "--project",
            "Integration Test Project 2",
            "--experiment",
            "integration-test-experiment-2",
            "--benchmark",
            "integration-test-benchmark-2",
            "--reports-dir",
            str(tmp_path / "reports"),
        ]
    )

    experiment = db_session.scalar(
        select(Experiment).where(Experiment.name == "integration-test-experiment-2")
    )
    assert experiment is not None

    benchmark = db_session.scalar(
        select(Benchmark).where(
            Benchmark.experiment_id == experiment.id,
            Benchmark.name == "integration-test-benchmark-2",
        )
    )
    assert benchmark is not None
    assert benchmark.status == "completed"
    assert benchmark.completed_at is not None

    evaluations = db_session.scalars(
        select(Evaluation).where(Evaluation.benchmark_id == benchmark.id)
    ).all()

    assert len(evaluations) > 0
    for evaluation in evaluations:
        assert evaluation.query
        assert evaluation.answer


def test_pipeline_fails_gracefully_on_missing_dataset(tmp_path):
    run_evaluation = _load_run_evaluation_module()

    exit_code = run_evaluation.main(
        [
            "--dataset",
            str(tmp_path / "does-not-exist.json"),
            "--reports-dir",
            str(tmp_path / "reports"),
        ]
    )

    assert exit_code == 1
