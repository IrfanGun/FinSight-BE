import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy.orm import Session

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.modules.transactions.adapters.orm import FinancialAccountORM, TransactionCategoryORM
from app.modules.users.adapters.orm import UserORM
from app.shared.database import SessionLocal
from app.shared.security import hash_password


DEFAULT_USER = {
    "full_name": "FinSight Admin",
    "email": "admin@finsight.local",
    "role": "admin",
    "status": "active",
}

DEFAULT_CATEGORIES = [
    {"user_id": None, "name": "Salary", "type": "income", "icon": "wallet", "color": "green", "is_default": True, "is_active": True},
    {"user_id": None, "name": "Bonus", "type": "income", "icon": "gift", "color": "blue", "is_default": True, "is_active": True},
    {"user_id": None, "name": "Food", "type": "expense", "icon": "utensils", "color": "orange", "is_default": True, "is_active": True},
    {"user_id": None, "name": "Transport", "type": "expense", "icon": "car", "color": "gray", "is_default": True, "is_active": True},
]

DEFAULT_ACCOUNTS = [
    {
        "name": "Cash Wallet",
        "type": "cash",
        "subtype": "wallet",
        "currency": "IDR",
        "balance": Decimal("0"),
        "unit": None,
        "quantity": None,
        "is_active": True,
    },
    {
        "name": "Main Bank Account",
        "type": "bank",
        "subtype": "checking",
        "currency": "IDR",
        "balance": Decimal("0"),
        "unit": None,
        "quantity": None,
        "is_active": True,
    },
]


def seed_default_user(db: Session) -> UserORM:
    existing = db.query(UserORM).filter(UserORM.email == DEFAULT_USER["email"]).first()
    if existing:
        return existing

    user = UserORM(
        full_name=DEFAULT_USER["full_name"],
        email=DEFAULT_USER["email"],
        password_hash=hash_password("admin123"),
        role=DEFAULT_USER["role"],
        status=DEFAULT_USER["status"],
    )
    db.add(user)
    db.flush()
    return user


def seed_transaction_categories(db: Session) -> None:
    for payload in DEFAULT_CATEGORIES:
        query = db.query(TransactionCategoryORM).filter(TransactionCategoryORM.name == payload["name"])
        if payload["user_id"] is None:
            query = query.filter(TransactionCategoryORM.user_id.is_(None))
        else:
            query = query.filter(TransactionCategoryORM.user_id == payload["user_id"])

        existing = query.first()
        if not existing:
            db.add(TransactionCategoryORM(**payload))


def seed_financial_accounts(db: Session, user_id: int) -> None:
    for base_payload in DEFAULT_ACCOUNTS:
        payload = dict(base_payload)
        payload["user_id"] = user_id
        existing = (
            db.query(FinancialAccountORM)
            .filter(
                FinancialAccountORM.name == payload["name"],
                FinancialAccountORM.user_id == user_id,
            )
            .first()
        )
        if not existing:
            db.add(FinancialAccountORM(**payload))


def main() -> None:
    db = SessionLocal()
    try:
        user = seed_default_user(db)
        seed_transaction_categories(db)
        seed_financial_accounts(db, user.id)
        db.commit()
        print("Seed completed")
    finally:
        db.close()


if __name__ == "__main__":
    main()
