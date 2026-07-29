from abc import ABC, abstractmethod


class BaseLLMClient(ABC):

    @abstractmethod
    def evaluate(
        self,
        prompt: str,
    ) -> str:
        """Evaluate a prompt and return the raw LLM response."""
        pass
