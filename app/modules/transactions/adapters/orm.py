from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.sql import func

from app.shared.database import Base


sqlite_bigint = BigInteger().with_variant(Integer, "sqlite")


class TransactionCategoryORM(Base):
    __tablename__ = "transaction_categories"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    name = Column(String(100), nullable=False)
    type = Column(String(30), nullable=False)
    icon = Column(String(100), nullable=True)
    color = Column(String(20), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class FinancialAccountORM(Base):
    __tablename__ = "finance_accounts"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    name = Column(String(150), nullable=True)
    type = Column(String(50), nullable=True)
    subtype = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=False, default="IDR")
    balance = Column(Numeric(18, 2), nullable=False, default=0)
    unit = Column(String(20), nullable=True)
    quantity = Column(Numeric(18, 4), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class TransactionORM(Base):
    __tablename__ = "transactions"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    from_account_id = Column(BigInteger, nullable=True)
    to_account_id = Column(BigInteger, nullable=True)
    category_id = Column(BigInteger, nullable=True)
    type = Column(String(30), nullable=True)
    amount = Column(Numeric(18, 2), nullable=False)
    transaction_date = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BudgetPlanORM(Base):
    __tablename__ = "budget_plans"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    category_id = Column(BigInteger, nullable=True)
    name = Column(String(150), nullable=False)
    amount_limit = Column(Numeric(18, 2), nullable=False)
    period_type = Column(String(30), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(String(30), nullable=True, default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AIConversationORM(Base):
    __tablename__ = "ai_conversations"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    title = Column(String(150), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AIMessageORM(Base):
    __tablename__ = "ai_messages"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    role = Column(String(30), nullable=False)
    message = Column(Text, nullable=False)
    intent = Column(String(100), nullable=True)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


class AIInsightORM(Base):
    __tablename__ = "ai_insights"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    insight_type = Column(String(100), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    severity = Column(String(30), nullable=True, default="info")
    is_read = Column(Boolean, nullable=True, default=False)
    created_at = Column(DateTime, server_default=func.now())

# Embedded Repository Implementations
class TransactionEmbeddingORM(Base):
    __tablename__ = "transaction_embeddings"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    transaction_id = Column(BigInteger, ForeignKey("transactions.id"), nullable=False)
    embedding = Column(JSON, nullable=False)
    document = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
