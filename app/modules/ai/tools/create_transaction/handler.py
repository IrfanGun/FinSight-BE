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
        fields = {error["loc"][0] for error in exc.errors()}
        questions = []
        if "amount" in fields:
            questions.append("berapa nominalnya")
        if "account_name" in fields:
            questions.append("menggunakan akun apa")
        if "category_name" in fields:
            questions.append("masuk kategori apa")

        question = " dan ".join(questions)
        return {
            "success": False,
            "message": (
                f"Saya perlu konfirmasi: {question}."
                if question
                else "Saya perlu konfirmasi detail transaksi tersebut."
            ),
            "error_code": "INVALID_TOOL_ARGUMENTS",
            "requires_clarification": True,
            "next_action": "CONFIRM_TRANSACTION_DETAILS",
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
                f"Akun '{validated.account_name}' belum ditemukan. "
                f"Apakah ingin membuat akun/aset '{validated.account_name}'?"
            ),
            "error_code": "ACCOUNT_NOT_FOUND",
            "requires_clarification": True,
            "next_action": "CREATE_FINANCIAL_ACCOUNT",
            "data": {"account_name": validated.account_name},
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
                "belum ditemukan. Apakah ingin membuat kategori "
                f"'{validated.category_name}'?"
            ),
            "error_code": "CATEGORY_NOT_FOUND",
            "requires_clarification": True,
            "next_action": "CREATE_TRANSACTION_CATEGORY",
            "data": {"category_name": validated.category_name},
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
