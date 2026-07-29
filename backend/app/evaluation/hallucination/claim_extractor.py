from abc import ABC, abstractmethod

from app.llm.client import LLMClient


class BaseClaimExtractor(ABC):
    """
    Base interface for claim extraction.
    """

    @abstractmethod
    def extract(
        self,
        answer: str,
    ) -> list[str]:
        """
        Extract factual claims from an answer.
        """
        raise NotImplementedError


class LLMClaimExtractor(BaseClaimExtractor):
    """
    Uses an LLM to extract factual claims.
    """

    def __init__(self):
        self.client = LLMClient()

    def extract(
        self,
        answer: str,
    ) -> list[str]:

        if not answer.strip():
            return []

        prompt = f"""
You are an information extraction assistant.

Extract ONLY factual claims from the answer.

Rules:

- One claim per line.
- Preserve wording.
- Ignore opinions.
- Ignore greetings.
- Ignore explanations.
- Return plain text only.
- No numbering.
- No markdown.

Answer:

{answer}
"""

        response = self.client.evaluate(prompt)

        claims = [line.strip() for line in response.splitlines() if line.strip()]

        return claims
