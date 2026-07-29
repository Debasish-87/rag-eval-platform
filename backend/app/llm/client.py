from app.core.config import settings
from app.llm.base import BaseLLMClient
from app.llm.mock import MockLLMClient


class LLMClient:
    """Factory for selecting the configured LLM provider."""

    _PROVIDERS: dict[str, type[BaseLLMClient]] = {
        "mock": MockLLMClient,
    }

    def __init__(self) -> None:
        provider = settings.LLM_PROVIDER.lower()

        if provider == "gemini":
            # Imported lazily: the google-genai SDK is an optional,
            # heavier dependency only needed when a real LLM judge
            # is configured.
            from app.llm.gemini import GeminiClient

            self._PROVIDERS.setdefault("gemini", GeminiClient)

        try:
            self.client = self._PROVIDERS[provider]()
        except KeyError as exc:
            supported = ", ".join(sorted(self._PROVIDERS.keys()))
            raise ValueError(
                f"Unsupported LLM provider '{provider}'. "
                f"Supported providers: {supported}"
            ) from exc

    def evaluate(
        self,
        prompt: str,
    ) -> str:
        return self.client.evaluate(prompt)
