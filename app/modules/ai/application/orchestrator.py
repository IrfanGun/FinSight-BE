from typing import Any

from app.modules.ai.adapters.repository import AIConversationRepository
from app.modules.ai.application.llm_client import GroqLLMClient
from app.modules.ai.application.prompt_builder import PromptBuilder
from app.modules.ai.application.tool_dispatcher import ToolDispatcher
from app.modules.ai.application.unit_of_work import UnitOfWork


class FinanceOrchestrator:
    def __init__(self, *, transaction_service, account_service, category_service,
                 conversation_repository: AIConversationRepository) -> None:
        self.repository = conversation_repository
        self.uow = UnitOfWork(conversation_repository)
        self.llm = GroqLLMClient()
        self.prompt_builder = PromptBuilder()
        self.tools = ToolDispatcher(
            transaction_service=transaction_service,
            account_service=account_service,
            category_service=category_service,
        )

    def process(self, *, user_id: int, conversation_id: int | None,
                message: str) -> dict[str, Any]:
        conversation = self.repository.get_or_create(
            user_id=user_id, conversation_id=conversation_id
        )
        self.repository.add_message(
            conversation_id=conversation.id, user_id=user_id,
            role="user", message=message,
        )
        history = self.repository.get_recent_messages(
            conversation_id=conversation.id, user_id=user_id
        )
        correction = PromptBuilder.correction(message, history)
        if correction is not None:
            result = self.tools.dispatch_correction(correction, user_id=user_id)
        else:
            response = self.llm.generate(
                messages=PromptBuilder.build(history), tools=ToolDispatcher.TOOLS
            )
            assistant = response.choices[0].message
            if assistant.tool_calls:
                result = self.tools.dispatch(tool_call=assistant.tool_calls[0], user_id=user_id)
            else:
                result = {
                    "success": True, "route": "chat", "tool_name": None,
                    "message": assistant.content or "Saya belum menemukan transaksi untuk dicatat.",
                    "data": None,
                }
        result["conversation_id"] = conversation.id
        return self._save_response(conversation.id, user_id, result)

    def _save_response(self, conversation_id: int, user_id: int,
                       response: dict[str, Any]) -> dict[str, Any]:
        self.repository.add_message(
            conversation_id=conversation_id, user_id=user_id, role="assistant",
            message=response["message"], intent=response.get("tool_name"),
            metadata={"route": response.get("route"), "data": response.get("data")},
        )
        self.uow.commit()
        return response
