import json
from typing import Any

from app.modules.ai.tools.create_transaction.definition import CREATE_TRANSACTION_TOOL
from app.modules.ai.tools.create_transaction.handler import execute_create_transaction
from app.modules.ai.tools.delete_transaction.definition import DELETE_TRANSACTION_TOOL
from app.modules.ai.tools.delete_transaction.handler import execute_delete_transaction
from app.modules.ai.tools.update_transaction.definition import UPDATE_TRANSACTION_TOOL
from app.modules.ai.tools.update_transaction.handler import execute_update_transaction


class ToolDispatcher:
    TOOLS = [CREATE_TRANSACTION_TOOL, UPDATE_TRANSACTION_TOOL, DELETE_TRANSACTION_TOOL]

    def __init__(self, *, transaction_service, account_service, category_service):
        self.services = (transaction_service, account_service, category_service)
        self.handlers = {
            "create_transaction": execute_create_transaction,
            "update_transaction": execute_update_transaction,
            "delete_transaction": execute_delete_transaction,
        }

    def dispatch(self, *, tool_call, user_id: int) -> dict[str, Any]:
        name = tool_call.function.name
        handler = self.handlers.get(name)
        if handler is None:
            return {"success": False, "route": "blocked", "tool_name": name,
                    "message": f"Tool '{name}' tidak diizinkan.", "data": None}
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return {"success": False, "route": "error", "tool_name": name,
                    "message": "Groq menghasilkan parameter tool yang tidak valid.",
                    "data": None}
        transaction_service, account_service, category_service = self.services
        return {"route": "tool", "tool_name": name, **handler(
            arguments=arguments, user_id=user_id, transaction_service=transaction_service,
            account_service=account_service, category_service=category_service,
        )}

    def dispatch_correction(self, arguments: dict, *, user_id: int) -> dict[str, Any]:
        transaction_service, account_service, category_service = self.services
        return {"route": "tool", "tool_name": "update_transaction", **execute_update_transaction(
            arguments=arguments, user_id=user_id, transaction_service=transaction_service,
            account_service=account_service, category_service=category_service,
        )}
