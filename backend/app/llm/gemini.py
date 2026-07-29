from google import genai
from google.genai import types

from app.core.config import settings
from app.llm.base import BaseLLMClient


class GeminiClient(BaseLLMClient):
    """Gemini implementation of the LLM client."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )
        self.model = settings.GEMINI_MODEL

    def evaluate(
        self,
        prompt: str,
    ) -> str:
        """
        Generate an evaluation response from Gemini.

        Args:
            prompt: Prompt sent to the model.

        Returns:
            The model response as plain text.

        Raises:
            RuntimeError: If Gemini returns an empty response.
            Exception: Propagates SDK/API errors.
        """
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
        except Exception as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text

    def health_check(self) -> bool:
        """
        Verify that the configured model is reachable.

        Returns:
            True if the model responds successfully.
        """
        try:
            self.client.models.generate_content(
                model=self.model,
                contents="ping",
            )
            return True
        except Exception:
            return False
