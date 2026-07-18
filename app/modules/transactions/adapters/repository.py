#modules/transactions/adapters/repository.py
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.transactions.adapters.orm import (
    FinancialAccountORM,
    TransactionEmbeddingORM,
    TransactionORM,
    TransactionCategoryORM,
)


class TransactionCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return (
            self.db.query(TransactionCategoryORM)
            .order_by(TransactionCategoryORM.id.desc())
            .all()
        )

    def get_by_id(self, category_id: int):
        return (
            self.db.query(TransactionCategoryORM)
            .filter(TransactionCategoryORM.id == category_id)
            .first()
        )

    def get_by_name(self, name: str, user_id: int | None = None):
        normalized_name = name.strip().lower()

        query = self.db.query(TransactionCategoryORM).filter(
            func.lower(TransactionCategoryORM.name)
            == normalized_name
        )

        if user_id is None:
            query = query.filter(
                TransactionCategoryORM.user_id.is_(None)
            )
        else:
            query = query.filter(
                TransactionCategoryORM.user_id == user_id
            )

        return query.first()

    def create(self, data: dict):
        category = TransactionCategoryORM(**data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category: TransactionCategoryORM, data: dict):
        for key, value in data.items():
            setattr(category, key, value)

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category: TransactionCategoryORM):
        self.db.delete(category)
        self.db.commit()
        return category


class FinancialAccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return (
            self.db.query(FinancialAccountORM)
            .order_by(FinancialAccountORM.id.desc())
            .all()
        )

    def get_by_id(self, account_id: int):
        return (
            self.db.query(FinancialAccountORM)
            .filter(FinancialAccountORM.id == account_id)
            .first()
        )

    def get_by_name(self, name: str, user_id: int):
        normalized_name = name.strip().lower()
        return self.db.query(FinancialAccountORM).filter(
            func.lower(FinancialAccountORM.name) == normalized_name,
            FinancialAccountORM.user_id == user_id,
        ).first()

    def create(self, data: dict):
        account = FinancialAccountORM(**data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update(self, account: FinancialAccountORM, data: dict):
        for key, value in data.items():
            setattr(account, key, value)

        self.db.commit()
        self.db.refresh(account)
        return account

    def delete(self, account: FinancialAccountORM):
        self.db.delete(account)
        self.db.commit()
        return account


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, transaction_id: int):
        return (
            self.db.query(TransactionORM)
            .filter(TransactionORM.id == transaction_id)
            .first()
        )

    def get_by_id_and_user_id(
        self,
        transaction_id: int,
        user_id: int,
    ):
        return (
            self.db.query(TransactionORM)
            .filter(
                TransactionORM.id == transaction_id,
                TransactionORM.user_id == user_id,
            )
            .first()
        )

    def get_latest_by_user_id(self, user_id: int):
        return (
            self.db.query(TransactionORM)
            .filter(TransactionORM.user_id == user_id)
            .order_by(
                TransactionORM.transaction_date.desc(),
                TransactionORM.id.desc(),
            )
            .first()
        )

    def find_candidates(
        self,
        *,
        user_id: int,
        amount=None,
        transaction_date=None,
        from_account_id=None,
        category_id=None,
        limit: int = 10,
    ):
        query = self.db.query(TransactionORM).filter(
            TransactionORM.user_id == user_id
        )

        if amount is not None:
            query = query.filter(TransactionORM.amount == amount)

        if transaction_date is not None:
            query = query.filter(
                TransactionORM.transaction_date == transaction_date
            )

        if from_account_id is not None:
            query = query.filter(
                TransactionORM.from_account_id == from_account_id
            )

        if category_id is not None:
            query = query.filter(
                TransactionORM.category_id == category_id
            )

        return (
            query.order_by(TransactionORM.transaction_date.desc(), TransactionORM.id.desc())
            .limit(limit)
            .all()
        )

    def create(self, data: dict):
        transaction = TransactionORM(**data)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def update(self, transaction: TransactionORM, data: dict):
        for key, value in data.items():
            setattr(transaction, key, value)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete(self, transaction: TransactionORM):
        self.db.delete(transaction)
        self.db.commit()
        return transaction


class TransactionEmbeddingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict):
        embedding = TransactionEmbeddingORM(**data)
        self.db.add(embedding)
        self.db.commit()
        self.db.refresh(embedding)
        return embedding
