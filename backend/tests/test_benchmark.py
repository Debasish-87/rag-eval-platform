from app.datasets.loader import DatasetLoader
from app.experiments.benchmark import BenchmarkRunner


def test_benchmark_runner_evaluates_every_sample(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)
    runner = BenchmarkRunner()

    result = runner.run(dataset)

    assert result.dataset_name == dataset.name
    assert result.total_samples == len(dataset)
    assert result.successful_samples == len(dataset)
    assert result.failed_samples == 0
    assert result.is_successful is True
    assert result.success_rate == 1.0


def test_benchmark_runner_computes_average_scores(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)
    runner = BenchmarkRunner()

    result = runner.run(dataset)

    expected_metrics = {
        "precision@2",
        "recall@2",
        "mrr",
        "hit_rate",
        "ndcg@2",
        "map@2",
        "faithfulness",
        "correctness",
        "semantic_similarity",
        "llm_faithfulness",
        "answer_relevance",
        "hallucination",
    }

    assert expected_metrics.issubset(result.average_scores.keys())

    for score in result.average_scores.values():
        assert 0.0 <= score <= 1.0


def test_benchmark_runner_tracks_duration(sample_dataset_path):
    dataset = DatasetLoader.load(sample_dataset_path)
    result = BenchmarkRunner().run(dataset)

    assert result.duration_ms >= 0
    assert result.completed_at is not None
    assert result.completed_at >= result.started_at
