from app.modules.ai.service_layer.embedding_service import EmbeddingService
from app.modules.ai.service_layer.vector_store import VectorStore
from app.modules.transactions.adapters.orm import TransactionORM
from app.modules.transactions.adapters.repository import (
    FinancialAccountRepository,
    TransactionRepository,
    TransactionCategoryRepository,
    TransactionEmbeddingRepository
)
from datetime import date, timedelta
from app.modules.transactions.domain.entities import TransactionUpdate


def _proportions(rows):
    total = sum((row.amount or 0 for row in rows), 0)
    return [{"label": row.label or "Uncategorized", "amount": row.amount or 0,
             "percentage": (row.amount or 0) * 100 / total if total else 0} for row in rows]


class TransactionCategoryService:
    def __init__(self, category_repo: TransactionCategoryRepository):
        self.category_repo = category_repo

    def get_all_categories(self):
        return self.category_repo.get_all()

    def get_category_by_id(self, category_id: int):
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Transaction category not found")
        return category

    def create_category(self, data):
        existing_category = self.category_repo.get_by_name(data.name, data.user_id)
        if existing_category:
            raise ValueError("Transaction category name already registered")

        return self.category_repo.create(data.model_dump())

    def update_category(self, category_id: int, data):
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Transaction category not found")

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data:
            target_user_id = update_data.get("user_id", category.user_id)
            existing_category = self.category_repo.get_by_name(update_data["name"], target_user_id)
            if existing_category and existing_category.id != category_id:
                raise ValueError("Transaction category name already used")

        return self.category_repo.update(category, update_data)

    def delete_category(self, category_id: int):
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError("Transaction category not found")

        return self.category_repo.delete(category)

    def find_category_by_name(
        self,
        name: str,
        user_id: int,
    ):
        category = self.category_repo.get_by_name(
            name=name,
            user_id=user_id,
        )

        if category is None:
            category = self.category_repo.get_by_name(
                name=name,
                user_id=None,
            )

        return category


class FinancialAccountService:
    def __init__(self, account_repo: FinancialAccountRepository):
        self.account_repo = account_repo

    def get_all_accounts(self):
        return self.account_repo.get_all()

    def get_assets(self, user_id: int):
        return self.account_repo.get_assets(user_id)

    def get_asset_proportions(self, user_id: int):
        return _proportions(self.account_repo.get_asset_proportions(user_id))

    def get_account_by_id(self, account_id: int):
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Financial account not found")
        return account

    def create_account(self, data):
        existing_account = self.account_repo.get_by_name(data.name, data.user_id)
        if existing_account:
            raise ValueError("Financial account name already registered")

        payload = data.model_dump()
        payload["currency"] = payload["currency"].upper()
        return self.account_repo.create(payload)

    def update_account(self, account_id: int, data):
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Financial account not found")

        update_data = data.model_dump(exclude_unset=True)

        if "name" in update_data:
            target_user_id = update_data.get("user_id", account.user_id)
            existing_account = self.account_repo.get_by_name(update_data["name"], target_user_id)
            if existing_account and existing_account.id != account_id:
                raise ValueError("Financial account name already used")

        if "currency" in update_data and update_data["currency"] is not None:
            update_data["currency"] = update_data["currency"].upper()

        return self.account_repo.update(account, update_data)

    def delete_account(self, account_id: int):
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Financial account not found")

        return self.account_repo.delete(account)
     
    def get_account_by_name(
        self,
        name: str,
        user_id: int,
    ):
        account = self.account_repo.get_by_name(
            name=name,
            user_id=user_id,
        )

        if not account:
            raise ValueError(
                f"Financial account '{name}' not found"
            )

        return account

    def find_account_by_name(
        self,
        name: str,
        user_id: int,
    ):
        return self.account_repo.get_by_name(
            name=name,
            user_id=user_id,
        )


class TransactionService:

    def get_category_proportions(self, user_id: int, transaction_type: str):
        return _proportions(self.transaction_repo.get_category_proportions(user_id, transaction_type))
    def __init__(
        self,
        transaction_repo: TransactionRepository,
        category_repo: TransactionCategoryRepository,
        account_repo: FinancialAccountRepository,
        embedding_service: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.transaction_repo = transaction_repo
        self.category_repo = category_repo
        self.account_repo = account_repo
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    @staticmethod
    def _build_transaction_document(transaction: TransactionORM) -> str:
        return (
            f"Tanggal {transaction.transaction_date}, "
            f"user melakukan {transaction.type} sebesar {transaction.amount}. "
            f"Dari akun {transaction.from_account_id}. "
            f"Kategori {transaction.category_id}."
        )

    def _add_names(self, transaction):
        category = self.category_repo.get_by_id(transaction.category_id) if transaction.category_id else None
        account = self.account_repo.get_by_id(transaction.from_account_id) if transaction.from_account_id else None
        transaction.category_name = category.name if category else None
        transaction.from_account_name = account.name if account else None
        return transaction

    def _add_names_to_list(self, transactions):
        return [self._add_names(transaction) for transaction in transactions]

    def create_transaction(self, data):
        category = self.category_repo.get_by_id(data.category_id)
        if not category:
            raise ValueError("Transaction category not found")

        from_account = self.account_repo.get_by_id(data.from_account_id)
        if not from_account:
            raise ValueError("Financial account not found")

        if from_account.user_id != data.user_id:
            raise ValueError("Financial account does not belong to this user")

        payload = data.model_dump(exclude_unset=True)
        payload["type"] = category.type

        if not payload.get("transaction_date"):
            payload["transaction_date"] = date.today()

        transaction = self.transaction_repo.create(payload)

        document = self._build_transaction_document(transaction)
        embedding = self.embedding_service.embed(document)

        self.vector_store.add_document(
            documents=[document],
            embeddings=[embedding],
            ids=[f"transaction-{transaction.id}"]
        )

        return self._add_names(transaction)

    def get_transaction_by_id(
        self,
        transaction_id: int,
        user_id: int,
    ):
        transaction = self.transaction_repo.get_by_id_and_user_id(
            transaction_id=transaction_id,
            user_id=user_id,
        )
        if not transaction:
            raise ValueError("Transaction not found")
        return self._add_names(transaction)

    def get_transactions(self, user_id: int, limit: int = 100, offset: int = 0):
        return self._add_names_to_list(
            self.transaction_repo.get_all_by_user_id(user_id, limit, offset)
        )

    def get_summary(self, user_id: int, period: str = "monthly", target_date: date | None = None):
        target_date = target_date or date.today()
        if period == "daily":
            start_date = target_date
            end_date = start_date + timedelta(days=1)
        elif period == "weekly":
            start_date = target_date - timedelta(days=target_date.weekday())
            end_date = start_date + timedelta(days=7)
        elif period == "monthly":
            start_date = target_date.replace(day=1)
            end_date = (start_date.replace(year=start_date.year + 1, month=1)
                        if start_date.month == 12
                        else start_date.replace(month=start_date.month + 1))
        elif period == "yearly":
            start_date = target_date.replace(month=1, day=1)
            end_date = start_date.replace(year=start_date.year + 1)
        else:
            raise ValueError("period must be daily, weekly, monthly, or yearly")

        summary = self.transaction_repo.get_summary_by_user_id(
            user_id, start_date, end_date
        )
        return {
            "user_id": user_id,
            "period": period,
            "start_date": start_date,
            "end_date": end_date - timedelta(days=1),
            "income": summary.income,
            "expense": summary.expense,
            "balance": summary.income - summary.expense,
        }

    def get_latest_transaction(self, user_id: int):
        transaction = self.transaction_repo.get_latest_by_user_id(
            user_id=user_id,
        )
        if not transaction:
            raise ValueError("Transaction not found")
        return self._add_names(transaction)

    def find_transactions(
        self,
        *,
        user_id: int,
        amount=None,
        transaction_date=None,
        from_account_id=None,
        category_id=None,
        limit: int = 10,
    ):
        return self._add_names_to_list(self.transaction_repo.find_candidates(
            user_id=user_id,
            amount=amount,
            transaction_date=transaction_date,
            from_account_id=from_account_id,
            category_id=category_id,
            limit=limit,
        ))

    def update_transaction(
        self,
        transaction_id: int,
        user_id: int,
        data: TransactionUpdate,
    ):
        transaction = self.get_transaction_by_id(transaction_id, user_id)

        update_data = data.model_dump(exclude_unset=True)

        if "category_id" in update_data and update_data["category_id"] is not None:
            category = self.category_repo.get_by_id(update_data["category_id"])
            if not category:
                raise ValueError("Transaction category not found")
            update_data["type"] = category.type

        if "from_account_id" in update_data and update_data["from_account_id"] is not None:
            account = self.account_repo.get_by_id(update_data["from_account_id"])
            if not account:
                raise ValueError("Financial account not found")
            if account.user_id != user_id:
                raise ValueError("Financial account does not belong to this user")

        transaction = self.transaction_repo.update(transaction, update_data)

        document = self._build_transaction_document(transaction)
        embedding = self.embedding_service.embed(document)
        self.vector_store.upsert_document(
            documents=[document],
            embeddings=[embedding],
            ids=[f"transaction-{transaction.id}"],
        )

        return self._add_names(transaction)

    def delete_transaction(
        self,
        transaction_id: int,
        user_id: int,
    ):
        transaction = self.get_transaction_by_id(transaction_id, user_id)
        deleted = self.transaction_repo.delete(transaction)
        self.vector_store.delete_document([f"transaction-{transaction_id}"])
        return deleted
