from typing import Any

from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    conversation_id: int | None = Field(default=None, ge=1)
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=[
            "Hari ini saya membeli bensin 30 ribu menggunakan BCA"
        ],
    )


class AIChatResponse(BaseModel):
    success: bool
    conversation_id: int
    route: str
    message: str
    tool_name: str | None = None
    data: dict[str, Any] | None = None
