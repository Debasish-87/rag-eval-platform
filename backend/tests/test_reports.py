import csv
import json

from app.datasets.loader import DatasetLoader
from app.experiments.benchmark import BenchmarkRunner
from app.reports import CSVReport, JSONReport, MarkdownReport


def run_small_benchmark(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)
    return BenchmarkRunner().run(dataset)


def test_json_report_contains_average_scores(tmp_path, sample_dataset_path):
    result = run_small_benchmark(sample_dataset_path)
    out = tmp_path / "report.json"

    JSONReport().generate(result, out)

    assert out.exists()
    data = json.loads(out.read_text())
    assert data["dataset_name"] == result.dataset_name
    assert data["total_samples"] == result.total_samples
    assert set(data["average_scores"]) == set(result.average_scores)


def test_csv_report_has_one_row_per_sample(tmp_path, sample_dataset_path):
    result = run_small_benchmark(sample_dataset_path)
    out = tmp_path / "report.csv"

    CSVReport().generate(result, out)

    assert out.exists()
    with out.open() as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == result.total_samples


def test_markdown_report_includes_metric_table(tmp_path, sample_dataset_path):
    result = run_small_benchmark(sample_dataset_path)
    out = tmp_path / "report.md"

    MarkdownReport().generate(result, out)

    content = out.read_text()
    assert "# Benchmark Report" in content
    assert "## Average Scores" in content
    for metric_name in result.average_scores:
        assert metric_name in content
