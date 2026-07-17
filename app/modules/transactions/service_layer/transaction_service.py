from app.modules.ai.service_layer.embedding_service import EmbeddingService
from app.modules.ai.service_layer.vector_store import VectorStore
from app.modules.transactions.adapters.repository import (
    FinancialAccountRepository,
    TransactionRepository,
    TransactionCategoryRepository,
    TransactionEmbeddingRepository
)
from datetime import date


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

        document = (
            f"Tanggal {transaction.transaction_date}, "
            f"user melakukan {transaction.type} sebesar {transaction.amount}. "
            f"Judul: {getattr(transaction, 'title', '-') or '-'}. "
            f"Deskripsi: {getattr(transaction, 'description', '-') or '-'}."
        )

        embedding = self.embedding_service.embed(document)

        self.vector_store.add_document(
            documents=[document],
            embeddings=[embedding],
            ids=[f"transaction-{transaction.id}"]
        )

        return transaction
    
