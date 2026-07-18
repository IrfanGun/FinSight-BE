from typing import Any

from pydantic import ValidationError

from app.modules.ai.tools.shared import resolve_transaction_target
from app.modules.ai.tools.update_transaction.schema import (
    UpdateTransactionToolArguments,
)
from app.modules.transactions.domain.entities import TransactionUpdate
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionCategoryService,
    TransactionService,
)


def _serialize_validation_errors(exc: ValidationError) -> list[dict[str, Any]]:
    errors = []
    for error in exc.errors():
        safe_error = dict(error)
        if "ctx" in safe_error:
            safe_error["ctx"] = {
                key: str(value)
                for key, value in safe_error["ctx"].items()
            }
        errors.append(safe_error)
    return errors


def execute_update_transaction(
    *,
    arguments: dict[str, Any],
    user_id: int,
    transaction_service: TransactionService,
    account_service: FinancialAccountService,
    category_service: TransactionCategoryService,
) -> dict[str, Any]:
    try:
        validated = UpdateTransactionToolArguments.model_validate(arguments)
    except ValidationError as exc:
        return {
            "success": False,
            "message": "Parameter update transaksi dari LLM tidak valid.",
            "error_code": "INVALID_TOOL_ARGUMENTS",
            "data": {
                "details": _serialize_validation_errors(exc),
            },
        }

    has_target_reference = any(
        [
            validated.transaction_id is not None,
            validated.reference_amount is not None,
            validated.reference_account_name,
            validated.reference_category_name,
            validated.reference_transaction_date is not None,
        ]
    )

    if has_target_reference:
        target = resolve_transaction_target(
            transaction_service=transaction_service,
            account_service=account_service,
            category_service=category_service,
            user_id=user_id,
            transaction_id=validated.transaction_id,
            amount=validated.reference_amount,
            account_name=validated.reference_account_name,
            category_name=validated.reference_category_name,
            transaction_date=validated.reference_transaction_date,
        )
    else:
        try:
            target = {
                "success": True,
                "transaction": transaction_service.get_latest_transaction(
                    user_id=user_id,
                ),
            }
        except ValueError:
            target = {
                "success": False,
                "message": (
                    "Saya belum menemukan transaksi terakhir yang bisa dikoreksi."
                ),
                "error_code": "TRANSACTION_NOT_FOUND",
                "requires_clarification": True,
            }

    if not target["success"]:
        return target

    account_id = None
    account_name = None
    if validated.account_name:
        account = account_service.find_account_by_name(
            name=validated.account_name,
            user_id=user_id,
        )
        if account is None:
            return {
                "success": False,
                "message": f"Akun '{validated.account_name}' tidak ditemukan.",
                "error_code": "ACCOUNT_NOT_FOUND",
                "requires_clarification": True,
            }
        account_id = account.id
        account_name = account.name

    category_id = None
    category_name = None
    if validated.category_name:
        category = category_service.find_category_by_name(
            name=validated.category_name,
            user_id=user_id,
        )
        if category is None:
            return {
                "success": False,
                "message": f"Kategori '{validated.category_name}' tidak ditemukan.",
                "error_code": "CATEGORY_NOT_FOUND",
                "requires_clarification": True,
            }
        category_id = category.id
        category_name = category.name

    update_payload = {}
    if category_id is not None:
        update_payload["category_id"] = category_id
    if account_id is not None:
        update_payload["from_account_id"] = account_id
    if validated.amount is not None:
        update_payload["amount"] = validated.amount
    if validated.transaction_date is not None:
        update_payload["transaction_date"] = validated.transaction_date

    payload = TransactionUpdate(**update_payload)

    try:
        transaction = transaction_service.update_transaction(
            transaction_id=target["transaction"].id,
            user_id=user_id,
            data=payload,
        )
    except ValueError as exc:
        return {
            "success": False,
            "message": str(exc),
            "error_code": "UPDATE_TRANSACTION_FAILED",
        }

    return {
        "success": True,
        "message": (
            f"Transaksi {transaction.id} berhasil diperbarui."
        ),
        "data": {
            "id": transaction.id,
            "user_id": transaction.user_id,
            "category_id": transaction.category_id,
            "category_name": category_name,
            "from_account_id": transaction.from_account_id,
            "account_name": account_name,
            "amount": float(transaction.amount),
            "transaction_date": (
                transaction.transaction_date.isoformat()
                if transaction.transaction_date
                else None
            ),
        },
    }
