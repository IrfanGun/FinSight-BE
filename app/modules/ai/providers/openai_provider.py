# app/ai/providers/openai_provider.py

from typing import Any

from openai import AsyncOpenAI

from app.core.config import get_settings


class OpenAIProvider:
    def __init__(self) -> None:
        settings = get_settings()

        self.model = settings.openai_model
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
        )

    async def create_response(
        self,
        *,
        system_prompt: str,
        user_message: str,
        tools: list[dict[str, Any]],
    ):
        return await self.client.responses.create(
            model=self.model,
            instructions=system_prompt,
            input=user_message,
            tools=tools,
            tool_choice="auto",
        )