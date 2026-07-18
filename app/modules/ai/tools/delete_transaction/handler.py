from typing import Any

from pydantic import ValidationError

from app.modules.ai.tools.delete_transaction.schema import (
    DeleteTransactionToolArguments,
)
from app.modules.ai.tools.shared import resolve_transaction_target
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionCategoryService,
    TransactionService,
)


def execute_delete_transaction(
    *,
    arguments: dict[str, Any],
    user_id: int,
    transaction_service: TransactionService,
    account_service: FinancialAccountService,
    category_service: TransactionCategoryService,
) -> dict[str, Any]:
    try:
        validated = DeleteTransactionToolArguments.model_validate(arguments)
    except ValidationError as exc:
        return {
            "success": False,
            "message": "Parameter hapus transaksi dari LLM tidak valid.",
            "error_code": "INVALID_TOOL_ARGUMENTS",
            "details": exc.errors(),
        }

    target = resolve_transaction_target(
        transaction_service=transaction_service,
        account_service=account_service,
        category_service=category_service,
        user_id=user_id,
        transaction_id=validated.transaction_id,
        amount=validated.amount,
        account_name=validated.account_name,
        category_name=validated.category_name,
        transaction_date=validated.transaction_date,
    )
    if not target["success"]:
        return target

    transaction = target["transaction"]

    try:
        transaction_service.delete_transaction(
            transaction_id=transaction.id,
            user_id=user_id,
        )
    except ValueError as exc:
        return {
            "success": False,
            "message": str(exc),
            "error_code": "DELETE_TRANSACTION_FAILED",
        }

    return {
        "success": True,
        "message": f"Transaksi {transaction.id} berhasil dihapus.",
        "data": {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "category_id": transaction.category_id,
            "from_account_id": transaction.from_account_id,
            "amount": float(transaction.amount),
            "transaction_date": (
                transaction.transaction_date.isoformat()
                if transaction.transaction_date
                else None
            ),
        },
    }
