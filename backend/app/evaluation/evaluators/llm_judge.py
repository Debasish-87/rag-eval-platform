from app.core.config import settings
from app.evaluation.evaluator import BaseEvaluator
from app.evaluation.models import (
    EvaluationRequest,
    EvaluatorResult,
    MetricResult,
)
from app.llm.client import LLMClient
from app.llm.parser import LLMResponseParser


class LLMJudgeEvaluator(BaseEvaluator):
    """
    Evaluates RAG responses using an LLM as a judge.
    """

    def __init__(self) -> None:
        self.client = LLMClient()

    def evaluate(
        self,
        request: EvaluationRequest,
    ) -> EvaluatorResult:
        """
        Evaluate a generated answer using an LLM.
        """

        prompt = f"""
You are an expert RAG evaluation assistant.

Evaluate the generated answer using ONLY the retrieved context.

Instructions:

- Score each metric between 0.0 and 1.0.
- Do NOT use outside knowledge.
- If the answer contains unsupported facts, increase hallucination.
- Return ONLY valid JSON.
- Do NOT wrap the JSON in markdown.
- Do NOT include explanations outside the JSON.

Question:
{request.query}

Retrieved Context:
{chr(10).join(request.contexts)}

Generated Answer:
{request.answer}

Return exactly this JSON schema:

{{
    "faithfulness": 0.0,
    "answer_relevance": 0.0,
    "hallucination": 0.0,
    "reason": ""
}}
"""
        
        try:
            response = self.client.evaluate(prompt)

        except Exception as exc:
            return EvaluatorResult(
                evaluator="LLMJudgeEvaluator",
                metrics=[
                    MetricResult(
                        name="llm_faithfulness",
                        score=0.0,
                    ),
                    MetricResult(
                        name="answer_relevance",
                        score=0.0,
                    ),
                    MetricResult(
                        name="hallucination",
                        score=1.0,
                    ),
                ],
                metadata={
                    "provider": settings.LLM_PROVIDER,
                    "model": settings.GEMINI_MODEL,
                    "error": str(exc),
                },
            )

        try:
            result = LLMResponseParser.parse(response)

        except ValueError as exc:

            metadata = {
                "provider": settings.LLM_PROVIDER,
                "model": settings.GEMINI_MODEL,
                "error": str(exc),
            }

            if settings.DEBUG:
                metadata["prompt"] = prompt
                metadata["raw_response"] = response

            return EvaluatorResult(
                evaluator="LLMJudgeEvaluator",
                metrics=[
                    MetricResult(
                        name="llm_faithfulness",
                        score=0.0,
                    ),
                    MetricResult(
                        name="answer_relevance",
                        score=0.0,
                    ),
                    MetricResult(
                        name="hallucination",
                        score=1.0,
                    ),
                ],
                metadata=metadata,
            )

        metadata = {
            "reason": result["reason"],
            "provider": settings.LLM_PROVIDER,
            "model": settings.GEMINI_MODEL,
        }

        if settings.DEBUG:
            metadata["prompt"] = prompt
            metadata["raw_response"] = response

        return EvaluatorResult(
            evaluator="LLMJudgeEvaluator",
            metrics=[
                MetricResult(
                    name="llm_faithfulness",
                    score=float(result["faithfulness"]),
                ),
                MetricResult(
                    name="answer_relevance",
                    score=float(result["answer_relevance"]),
                ),
                MetricResult(
                    name="hallucination",
                    score=float(result["hallucination"]),
                ),
            ],
            metadata=metadata,
        )

    def _build_batch_prompt(
        self,
        requests: list[EvaluationRequest],
    ) -> str:

        items = []

        for index, request in enumerate(requests, start=1):
            items.append(
                f"""
    Item {index}

    Question:
    {request.query}

    Retrieved Context:
    {chr(10).join(request.contexts)}

    Generated Answer:
    {request.answer}
    """
            )

        return f"""
    You are an expert RAG evaluation assistant.

    Evaluate every item independently.

    Rules:

    - Use ONLY the retrieved context.
    - Score between 0.0 and 1.0.
    - Return ONLY valid JSON.
    - Do NOT use markdown.
    - Return a JSON array.

    Return exactly {len(requests)} JSON objects.

    The first object corresponds to Item 1.
    The second object corresponds to Item 2.
    Continue in the same order.
    Do not omit, reorder, or merge items.

    Example:

    [
    {{
        "faithfulness": 0.0,
        "answer_relevance": 0.0,
        "hallucination": 0.0,
        "reason": ""
    }}
    ]

    Items:

    {chr(10).join(items)}
    """

    def evaluate_batch(
        self,
        requests: list[EvaluationRequest],
    ) -> list[EvaluatorResult]:
        """
        Evaluate multiple requests in a single LLM call.
        """

        if not requests:
            return []

        prompt = self._build_batch_prompt(requests)
        # print(f"Calling Gemini for batch of {len(requests)} requests")

        try:
            response = self.client.evaluate(prompt)

        except Exception as exc:

            results = []

            for _ in requests:

                results.append(
                    EvaluatorResult(
                        evaluator="LLMJudgeEvaluator",
                        metrics=[
                            MetricResult(
                                name="llm_faithfulness",
                                score=0.0,
                            ),
                            MetricResult(
                                name="answer_relevance",
                                score=0.0,
                            ),
                            MetricResult(
                                name="hallucination",
                                score=1.0,
                            ),
                        ],
                        metadata={
                            "provider": settings.LLM_PROVIDER,
                            "model": settings.GEMINI_MODEL,
                            "error": str(exc),
                        },
                    )
                )

            return results

        try:
            parsed_results = LLMResponseParser.parse_batch(response)

        except ValueError as exc:

            results = []

            for _ in requests:

                metadata = {
                    "provider": settings.LLM_PROVIDER,
                    "model": settings.GEMINI_MODEL,
                    "error": str(exc),
                }

                if settings.DEBUG:
                    metadata["prompt"] = prompt
                    metadata["raw_response"] = response

                results.append(
                    EvaluatorResult(
                        evaluator="LLMJudgeEvaluator",
                        metrics=[
                            MetricResult(
                                name="llm_faithfulness",
                                score=0.0,
                            ),
                            MetricResult(
                                name="answer_relevance",
                                score=0.0,
                            ),
                            MetricResult(
                                name="hallucination",
                                score=1.0,
                            ),
                        ],
                        metadata=metadata,
                    )
                )

            return results

        if len(parsed_results) != len(requests):

            results = []

            for _ in requests:

                results.append(
                    EvaluatorResult(
                        evaluator="LLMJudgeEvaluator",
                        metrics=[
                            MetricResult(
                                name="llm_faithfulness",
                                score=0.0,
                            ),
                            MetricResult(
                                name="answer_relevance",
                                score=0.0,
                            ),
                            MetricResult(
                                name="hallucination",
                                score=1.0,
                            ),
                        ],
                        metadata={
                            "provider": settings.LLM_PROVIDER,
                            "model": settings.GEMINI_MODEL,
                            "error": (
                                f"Expected {len(requests)} results, "
                                f"received {len(parsed_results)}."
                            ),
                        },
                    )
                )

            return results

        results = []

        for result in parsed_results:

            metadata = {
                "reason": result["reason"],
                "provider": settings.LLM_PROVIDER,
                "model": settings.GEMINI_MODEL,
            }

            if settings.DEBUG:
                metadata["prompt"] = prompt
                metadata["raw_response"] = response

            results.append(
                EvaluatorResult(
                    evaluator="LLMJudgeEvaluator",
                    metrics=[
                        MetricResult(
                            name="llm_faithfulness",
                            score=float(result["faithfulness"]),
                        ),
                        MetricResult(
                            name="answer_relevance",
                            score=float(result["answer_relevance"]),
                        ),
                        MetricResult(
                            name="hallucination",
                            score=float(result["hallucination"]),
                        ),
                    ],
                    metadata=metadata,
                )
            )

        return results
