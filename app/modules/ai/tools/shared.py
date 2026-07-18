from typing import Any

from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionCategoryService,
    TransactionService,
)


def resolve_transaction_target(
    *,
    transaction_service: TransactionService,
    account_service: FinancialAccountService,
    category_service: TransactionCategoryService,
    user_id: int,
    transaction_id: int | None = None,
    amount: Any = None,
    account_name: str | None = None,
    category_name: str | None = None,
    transaction_date: Any = None,
):
    if transaction_id is not None:
        try:
            return {
                "success": True,
                "transaction": transaction_service.get_transaction_by_id(
                    transaction_id=transaction_id,
                    user_id=user_id,
                ),
            }
        except ValueError:
            return {
                "success": False,
                "message": f"Transaksi dengan id {transaction_id} tidak ditemukan.",
                "error_code": "TRANSACTION_NOT_FOUND",
                "requires_clarification": True,
            }

    account = None
    if account_name:
        account = account_service.find_account_by_name(
            name=account_name,
            user_id=user_id,
        )
        if account is None:
            return {
                "success": False,
                "message": f"Akun '{account_name}' tidak ditemukan.",
                "error_code": "ACCOUNT_NOT_FOUND",
                "requires_clarification": True,
            }

    category = None
    if category_name:
        category = category_service.find_category_by_name(
            name=category_name,
            user_id=user_id,
        )
        if category is None:
            return {
                "success": False,
                "message": f"Kategori '{category_name}' tidak ditemukan.",
                "error_code": "CATEGORY_NOT_FOUND",
                "requires_clarification": True,
            }

    matches = transaction_service.find_transactions(
        user_id=user_id,
        amount=amount,
        transaction_date=transaction_date,
        from_account_id=getattr(account, "id", None),
        category_id=getattr(category, "id", None),
    )

    if not matches:
        return {
            "success": False,
            "message": (
                "Saya tidak menemukan transaksi yang cocok untuk diubah atau dihapus."
            ),
            "error_code": "TRANSACTION_NOT_FOUND",
            "requires_clarification": True,
        }

    if len(matches) > 1:
        candidate_ids = [item.id for item in matches[:5]]
        return {
            "success": False,
            "message": (
                "Saya menemukan lebih dari satu transaksi yang cocok. "
                f"Sebutkan transaction_id yang tepat. Kandidat: {candidate_ids}."
            ),
            "error_code": "AMBIGUOUS_TRANSACTION",
            "requires_clarification": True,
            "data": {
                "candidate_ids": candidate_ids,
            },
        }

    return {
        "success": True,
        "transaction": matches[0],
    }
