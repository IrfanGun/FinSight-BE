from sqlalchemy import Column, BigInteger, DateTime, Integer, String
from sqlalchemy.sql import func
from app.shared.database import Base


sqlite_bigint = BigInteger().with_variant(Integer, "sqlite")


class UserORM(Base):
    __tablename__ = "users"

    id = Column(sqlite_bigint, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    status = Column(String(30), default="active")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
