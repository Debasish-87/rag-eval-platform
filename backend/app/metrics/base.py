from abc import ABC, abstractmethod

from app.evaluation.models import EvaluationRequest


class BaseMetric(ABC):

    def __init__(self, **config):
        self.config = config

    @abstractmethod
    def compute(
        self,
        request: EvaluationRequest,
    ) -> float:
        pass
