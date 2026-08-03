from typing import Any

from app.modules.ai.providers.groq_provider import GroqProvider


class GroqLLMClient:
    """Application-facing adapter around the Groq SDK provider."""

    def __init__(self, provider: GroqProvider | None = None) -> None:
        self.provider = provider or GroqProvider()

    def generate(self, *, messages: list[dict[str, str]], tools: list[dict[str, Any]]):
        return self.provider.generate(messages=messages, tools=tools)
