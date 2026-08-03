from datetime import datetime
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


class AIMessageResponse(BaseModel):
    id: int
    role: str
    message: str
    intent: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None


class AIPaginatedMessagesResponse(BaseModel):
    items: list[AIMessageResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class AIConversationSummaryResponse(BaseModel):
    id: int
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AIPaginatedConversationsResponse(BaseModel):
    items: list[AIConversationSummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class AIConversationResponse(BaseModel):
    id: int
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[AIMessageResponse]
