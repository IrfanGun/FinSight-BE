# app/modules/ai/providers/groq_provider.py

from typing import Any

from groq import Groq

from app.shared.config import get_settings


class GroqProvider:
    def __init__(self) -> None:
        settings = get_settings()

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )
        self.model = settings.GROQ_MODEL

    def generate(
        self,
        *,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        tool_choice: str = "auto",
        temperature: float = 0,
    ):
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        return self.client.chat.completions.create(**payload)