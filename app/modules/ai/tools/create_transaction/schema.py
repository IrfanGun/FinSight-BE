from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CreateTransactionToolArguments(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=0,
        description="Nominal transaksi dalam angka penuh.",
    )

    account_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    category_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    transaction_date: date | None = None

    @field_validator("account_name", "category_name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()