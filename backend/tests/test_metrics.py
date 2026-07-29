import pytest

from app.evaluation.models import EvaluationRequest
from app.metrics.correctness import Correctness
from app.metrics.faithfulness import Faithfulness
from app.metrics.hit_rate import HitRate
from app.metrics.map import MAP
from app.metrics.mrr import MRR
from app.metrics.ndcg import NDCG
from app.metrics.precision import PrecisionAtK
from app.metrics.recall import RecallAtK
from app.metrics.semantic_similarity import SemanticSimilarity


def make_request(**overrides) -> EvaluationRequest:
    defaults = dict(
        query="Who created Python?",
        contexts=[
            "Python was created by Guido van Rossum.",
            "JavaScript was created by Brendan Eich.",
        ],
        answer="Python was created by Guido van Rossum.",
        ground_truth="Python was created by Guido van Rossum.",
        relevant_contexts=["Python was created by Guido van Rossum."],
    )
    defaults.update(overrides)
    return EvaluationRequest(**defaults)


class TestPrecisionAtK:
    def test_half_relevant(self):
        request = make_request()
        assert PrecisionAtK(k=2).compute(request) == 0.5

    def test_all_relevant(self):
        request = make_request(
            contexts=["A relevant fact.", "Another relevant fact."],
            relevant_contexts=["A relevant fact.", "Another relevant fact."],
        )
        assert PrecisionAtK(k=2).compute(request) == 1.0

    def test_no_contexts_returns_zero(self):
        request = make_request(contexts=[], relevant_contexts=[])
        assert PrecisionAtK(k=2).compute(request) == 0.0


class TestRecallAtK:
    def test_full_recall(self):
        request = make_request()
        assert RecallAtK(k=2).compute(request) == 1.0

    def test_no_relevant_returns_zero(self):
        request = make_request(relevant_contexts=[])
        assert RecallAtK(k=2).compute(request) == 0.0


class TestMRR:
    def test_first_result_relevant(self):
        request = make_request()
        assert MRR().compute(request) == 1.0

    def test_second_result_relevant(self):
        request = make_request(
            contexts=["Distractor.", "Python was created by Guido van Rossum."],
        )
        assert MRR().compute(request) == pytest.approx(0.5)

    def test_no_relevant_returns_zero(self):
        request = make_request(relevant_contexts=[])
        assert MRR().compute(request) == 0.0


class TestHitRate:
    def test_hit(self):
        request = make_request()
        assert HitRate().compute(request) == 1.0

    def test_miss(self):
        request = make_request(relevant_contexts=["Something else entirely."])
        assert HitRate().compute(request) == 0.0


class TestMAP:
    def test_perfect_ranking(self):
        request = make_request(
            contexts=["Python was created by Guido van Rossum.", "Distractor."],
        )
        assert MAP(k=2).compute(request) == pytest.approx(1.0)

    def test_no_hits_returns_zero(self):
        request = make_request(relevant_contexts=["Not present anywhere."])
        assert MAP(k=2).compute(request) == 0.0


class TestNDCG:
    def test_perfect_ranking_is_one(self):
        request = make_request(
            contexts=["Python was created by Guido van Rossum.", "Distractor."],
        )
        assert NDCG(k=2).compute(request) == pytest.approx(1.0)

    def test_no_relevant_returns_zero(self):
        request = make_request(relevant_contexts=[])
        assert NDCG(k=2).compute(request) == 0.0


class TestCorrectness:
    def test_exact_match(self):
        request = make_request()
        assert Correctness().compute(request) == 1.0

    def test_mismatch(self):
        request = make_request(answer="Something completely different.")
        assert Correctness().compute(request) == 0.0

    def test_no_ground_truth_returns_zero(self):
        request = make_request(ground_truth=None)
        assert Correctness().compute(request) == 0.0


class TestFaithfulness:
    def test_grounded_answer_scores_high(self):
        request = make_request()
        score = Faithfulness().compute(request)
        assert 0.5 <= score <= 1.0

    def test_unsupported_answer_scores_low(self):
        request = make_request(
            answer="Elephants migrate across the Sahara desert yearly.",
        )
        score = Faithfulness().compute(request)
        assert score < 0.3

    def test_empty_answer_returns_zero(self):
        request = make_request(answer="")
        assert Faithfulness().compute(request) == 0.0


class TestSemanticSimilarity:
    def test_identical_strings_score_high(self):
        request = make_request(
            answer="Python was created by Guido van Rossum.",
            ground_truth="Python was created by Guido van Rossum.",
        )
        assert SemanticSimilarity().compute(request) >= 0.5

    def test_no_ground_truth_returns_zero(self):
        request = make_request(ground_truth=None)
        assert SemanticSimilarity().compute(request) == 0.0

    def test_returns_bounded_score(self):
        request = make_request(
            answer="Completely unrelated statement about weather.",
        )
        score = SemanticSimilarity().compute(request)
        assert 0.0 <= score <= 1.0
