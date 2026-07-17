# app/modules/ai/tools/create_transaction/handler.py
from typing import Any

from pydantic import ValidationError

from app.modules.ai.tools.create_transaction.schema import (
    CreateTransactionToolArguments,
)
from app.modules.transactions.domain.entities import (
    TransactionCreate,
)
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionService,
    TransactionCategoryService,
)


def execute_create_transaction(
    *,
    arguments: dict[str, Any],
    user_id: int,
    transaction_service: TransactionService,
    account_service: FinancialAccountService,
    category_service: TransactionCategoryService,
) -> dict[str, Any]:
    try:
        validated = CreateTransactionToolArguments.model_validate(
            arguments
        )

    except ValidationError as exc:
        return {
            "success": False,
            "message": "Parameter transaksi dari LLM tidak valid.",
            "error_code": "INVALID_TOOL_ARGUMENTS",
            "details": exc.errors(),
        }

    account = account_service.find_account_by_name(
        name=validated.account_name,
        user_id=user_id,
    )

    if account is None:
        return {
            "success": False,
            "message": (
                f"Akun '{validated.account_name}' tidak ditemukan."
            ),
            "error_code": "ACCOUNT_NOT_FOUND",
            "requires_clarification": True,
        }

    category = category_service.find_category_by_name(
        name=validated.category_name,
        user_id=user_id,
    )

    if category is None:
        return {
            "success": False,
            "message": (
                f"Kategori '{validated.category_name}' "
                "tidak ditemukan."
            ),
            "error_code": "CATEGORY_NOT_FOUND",
            "requires_clarification": True,
        }

    transaction_data = TransactionCreate(
        user_id=user_id,
        category_id=category.id,
        from_account_id=account.id,
        amount=validated.amount,
        transaction_date=validated.transaction_date,
    )

    try:
        transaction = transaction_service.create_transaction(
            transaction_data
        )

    except ValueError as exc:
        return {
            "success": False,
            "message": str(exc),
            "error_code": "CREATE_TRANSACTION_FAILED",
        }

    return {
        "success": True,
        "message": (
            f"Pengeluaran sebesar Rp"
            f"{transaction.amount:,.0f} berhasil dicatat."
        ).replace(",", "."),
        "data": {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "category_id": transaction.category_id,
            "category_name": category.name,
            "from_account_id": transaction.from_account_id,
            "account_name": account.name,
            "amount": float(transaction.amount),
            "transaction_date": (
                transaction.transaction_date.isoformat()
                if transaction.transaction_date
                else None
            ),
        },
    }
