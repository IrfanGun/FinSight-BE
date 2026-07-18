from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class DeleteTransactionToolArguments(BaseModel):
    transaction_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    account_name: str | None = Field(default=None, min_length=1, max_length=100)
    category_name: str | None = Field(default=None, min_length=1, max_length=100)
    transaction_date: date | None = None

    @model_validator(mode="after")
    def validate_payload(self):
        if self.transaction_id is None and not any(
            [
                self.amount is not None,
                self.account_name,
                self.category_name,
                self.transaction_date is not None,
            ]
        ):
            raise ValueError(
                "transaction_id atau minimal satu field referensi wajib diisi."
            )
        return self
