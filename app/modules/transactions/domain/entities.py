from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


CategoryType = Literal["income", "expense"]


class TransactionCategoryCreate(BaseModel):
    user_id: Optional[int] = None
    name: str = Field(min_length=1, max_length=100)
    type: CategoryType
    icon: Optional[str] = Field(default=None, max_length=100)
    color: Optional[str] = Field(default=None, max_length=20)
    is_default: bool = False
    is_active: bool = True


class TransactionCategoryUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    type: Optional[CategoryType] = None
    icon: Optional[str] = Field(default=None, max_length=100)
    color: Optional[str] = Field(default=None, max_length=20)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class TransactionCategoryResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    name: str
    type: CategoryType
    icon: Optional[str] = None
    color: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FinancialAccountCreate(BaseModel):
    user_id: int
    name: str = Field(min_length=1, max_length=150)
    type: Optional[str] = Field(default=None, max_length=50)
    subtype: Optional[str] = Field(default=None, max_length=50)
    currency: str = Field(default="IDR", min_length=3, max_length=10)
    balance: Decimal = Field(default=Decimal("0"))
    unit: Optional[str] = Field(default=None, max_length=20)
    quantity: Optional[Decimal] = None
    is_active: bool = True


class FinancialAccountUpdate(BaseModel):
    user_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    type: Optional[str] = Field(default=None, max_length=50)
    subtype: Optional[str] = Field(default=None, max_length=50)
    currency: Optional[str] = Field(default=None, min_length=3, max_length=10)
    balance: Optional[Decimal] = None
    unit: Optional[str] = Field(default=None, max_length=20)
    quantity: Optional[Decimal] = None
    is_active: Optional[bool] = None


class FinancialAccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: Optional[str] = None
    subtype: Optional[str] = None
    currency: str
    balance: Decimal
    unit: Optional[str] = None
    quantity: Optional[Decimal] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    user_id: int
    category_id: int
    from_account_id: int
    amount: Decimal = Field(gt=0)
    transaction_date: Optional[date] = None


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    from_account_id: Optional[int] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    transaction_date: Optional[date] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    from_account_id: Optional[int] = None
    to_account_id: Optional[int] = None
    category_id: Optional[int] = None
    type: Optional[str] = None
    amount: Decimal
    transaction_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
