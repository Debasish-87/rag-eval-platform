from app.evaluation.engine import EvaluationEngine
from app.evaluation.models import EvaluationRequest


def make_request() -> EvaluationRequest:
    return EvaluationRequest(
        query="Who created Python?",
        contexts=[
            "Python was created by Guido van Rossum.",
            "Python was first released in 1991.",
        ],
        relevant_contexts=[
            "Python was created by Guido van Rossum.",
        ],
        answer="Python was created by Guido van Rossum.",
        ground_truth="Python was created by Guido van Rossum.",
    )


def test_engine_runs_every_registered_evaluator():
    engine = EvaluationEngine()
    result = engine.evaluate(make_request())

    evaluator_names = {e.evaluator for e in result.evaluators}

    assert evaluator_names == {
        "RetrievalEvaluator",
        "GenerationEvaluator",
        "LLMJudgeEvaluator",
    }


def test_engine_returns_typed_metric_scores():
    engine = EvaluationEngine()
    result = engine.evaluate(make_request())

    for evaluator_result in result.evaluators:
        assert (
            evaluator_result.metrics
        ), f"{evaluator_result.evaluator} produced no metrics"
        for metric in evaluator_result.metrics:
            assert isinstance(metric.name, str)
            assert isinstance(metric.score, float)


def test_engine_get_helper_finds_evaluator_by_name():
    engine = EvaluationEngine()
    result = engine.evaluate(make_request())

    retrieval = result.get("RetrievalEvaluator")
    assert retrieval is not None
    assert "precision@2" in retrieval.metric_dict()
