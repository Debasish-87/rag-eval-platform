from app.evaluation.evaluator import BaseEvaluator
from app.evaluation.evaluators.generation import (
    GenerationEvaluator,
)
from app.evaluation.evaluators.llm_judge import (
    LLMJudgeEvaluator,
)
from app.evaluation.evaluators.retrieval import (
    RetrievalEvaluator,
)


class EvaluatorRegistry:
    """
    Registry for all available evaluators.
    """

    _evaluators: list[type[BaseEvaluator]] = [
        RetrievalEvaluator,
        GenerationEvaluator,
        LLMJudgeEvaluator,
    ]

    @classmethod
    def get_evaluators(
        cls,
    ) -> list[BaseEvaluator]:
        """
        Return instances of all registered evaluators.
        """

        return [evaluator() for evaluator in cls._evaluators]

    @classmethod
    def register(
        cls,
        evaluator: type[BaseEvaluator],
    ) -> None:
        """
        Register a new evaluator.
        """

        if evaluator not in cls._evaluators:
            cls._evaluators.append(evaluator)

    @classmethod
    def unregister(
        cls,
        evaluator: type[BaseEvaluator],
    ) -> None:
        """
        Remove an evaluator from the registry.
        """

        if evaluator in cls._evaluators:
            cls._evaluators.remove(evaluator)

    @classmethod
    def clear(cls) -> None:
        """
        Remove all registered evaluators.
        """

        cls._evaluators.clear()
