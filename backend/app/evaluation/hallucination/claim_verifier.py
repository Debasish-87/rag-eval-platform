from abc import ABC, abstractmethod

from app.llm.client import LLMClient

from app.evaluation.hallucination.models import (
    ClaimResult,
    HallucinationResult,
)
from app.llm.parser import LLMResponseParser


class BaseClaimVerifier(ABC):

    @abstractmethod
    def verify(
        self,
        question: str,
        contexts: list[str],
        answer: str,
    ) -> HallucinationResult:
        raise NotImplementedError


class LLMClaimVerifier(BaseClaimVerifier):

    def __init__(self):
        self.client = LLMClient()

    def verify(
        self,
        question: str,
        contexts: list[str],
        answer: str,
    ) -> HallucinationResult:

        context = "\n".join(contexts)

        prompt = f"""
You are an expert RAG evaluator.

Task:

Analyze the generated answer using ONLY the retrieved context.

Return ONLY valid JSON.

JSON Schema:

{{
  "score": 0.0,
  "supported_claims": [
    {{
      "claim": "",
      "evidence": []
    }}
  ],
  "unsupported_claims": [
    {{
      "claim": "",
      "evidence": []
    }}
  ],
  "contradicted_claims": [
    {{
      "claim": "",
      "evidence": []
    }}
  ],
  "summary": ""
}}

Question:
{question}

Retrieved Context:
{context}

Generated Answer:
{answer}
"""

        response = self.client.evaluate(prompt)

        result = LLMResponseParser.parse(response)

        supported = [
            ClaimResult(
                claim=item["claim"],
                verdict="supported",
                evidence=item.get("evidence", []),
            )
            for item in result.get("supported_claims", [])
        ]

        unsupported = [
            ClaimResult(
                claim=item["claim"],
                verdict="unsupported",
                evidence=item.get("evidence", []),
            )
            for item in result.get("unsupported_claims", [])
        ]

        contradicted = [
            ClaimResult(
                claim=item["claim"],
                verdict="contradicted",
                evidence=item.get("evidence", []),
            )
            for item in result.get("contradicted_claims", [])
        ]

        return HallucinationResult(
            score=float(result["score"]),
            supported_claims=supported,
            unsupported_claims=unsupported,
            contradicted_claims=contradicted,
            summary=result["summary"],
        )
