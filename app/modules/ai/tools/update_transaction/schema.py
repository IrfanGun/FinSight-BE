from datetime import date
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class UpdateTransactionToolArguments(BaseModel):
    transaction_id: int | None = None
    reference_amount: Decimal | None = Field(default=None, gt=0)
    reference_account_name: str | None = Field(default=None, min_length=1, max_length=100)
    reference_category_name: str | None = Field(default=None, min_length=1, max_length=100)
    reference_transaction_date: date | None = None

    amount: Decimal | None = Field(default=None, gt=0)
    account_name: str | None = Field(default=None, min_length=1, max_length=100)
    category_name: str | None = Field(default=None, min_length=1, max_length=100)
    transaction_date: date | None = None

    @field_validator(
        "reference_account_name",
        "reference_category_name",
        "account_name",
        "category_name",
        mode="before",
    )
    @classmethod
    def empty_string_as_none(cls, value: Any):
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("reference_amount", "amount", mode="before")
    @classmethod
    def normalize_amount(cls, value: Any):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if not normalized:
                return None
            normalized = (
                normalized.replace("rp", "")
                .replace(".", "")
                .replace(",", ".")
                .strip()
            )
            multipliers = {
                "ribu": Decimal("1000"),
                "rb": Decimal("1000"),
                "juta": Decimal("1000000"),
                "jt": Decimal("1000000"),
            }
            for suffix, multiplier in multipliers.items():
                if normalized.endswith(suffix):
                    number = normalized[: -len(suffix)].strip()
                    return Decimal(number) * multiplier
            return Decimal(normalized)
        return value

    @model_validator(mode="after")
    def validate_payload(self):
        if not any(
            [
                self.amount is not None,
                self.account_name,
                self.category_name,
                self.transaction_date is not None,
            ]
        ):
            raise ValueError("Minimal satu field perubahan wajib diisi.")

        return self
