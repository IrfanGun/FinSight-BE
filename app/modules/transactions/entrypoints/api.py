from typing import List

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.modules.ai.service_layer.embedding_service import EmbeddingService
from app.modules.ai.service_layer.vector_store import VectorStore
from app.modules.transactions.adapters.repository import (
    FinancialAccountRepository,
    TransactionRepository,
    TransactionCategoryRepository,
)
from app.modules.transactions.domain.entities import (
    FinancialAccountCreate,
    FinancialAccountResponse,
    FinancialAccountUpdate,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    TransactionCategoryCreate,
    TransactionCategoryResponse,
    TransactionCategoryUpdate,
)
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionService,
    TransactionCategoryService,
)
from app.shared.database import get_db


router = APIRouter(tags=["Transactions"])


def get_transaction_category_service(db: Session = Depends(get_db)):
    return TransactionCategoryService(TransactionCategoryRepository(db))


def get_financial_account_service(db: Session = Depends(get_db)):
    return FinancialAccountService(FinancialAccountRepository(db))


def get_transaction_service(db: Session = Depends(get_db)):
    return TransactionService(
        TransactionRepository(db),
        TransactionCategoryRepository(db),
        FinancialAccountRepository(db),
        EmbeddingService(),
        VectorStore(),
    )


@router.get("/transaction-categories", response_model=List[TransactionCategoryResponse])
def get_transaction_categories(
    service: TransactionCategoryService = Depends(get_transaction_category_service),
):
    return service.get_all_categories()


@router.get("/transaction-categories/{category_id}", response_model=TransactionCategoryResponse)
def get_transaction_category(
    category_id: int,
    service: TransactionCategoryService = Depends(get_transaction_category_service),
):
    try:
        return service.get_category_by_id(category_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post(
    "/transaction-categories",
    response_model=TransactionCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction_category(
    data: TransactionCategoryCreate,
    service: TransactionCategoryService = Depends(get_transaction_category_service),
):
    try:
        return service.create_category(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/transaction-categories/{category_id}", response_model=TransactionCategoryResponse)
def update_transaction_category(
    category_id: int,
    data: TransactionCategoryUpdate,
    service: TransactionCategoryService = Depends(get_transaction_category_service),
):
    try:
        return service.update_category(category_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/transaction-categories/{category_id}", response_model=TransactionCategoryResponse)
def delete_transaction_category(
    category_id: int,
    service: TransactionCategoryService = Depends(get_transaction_category_service),
):
    try:
        return service.delete_category(category_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/finance-accounts", response_model=List[FinancialAccountResponse])
def get_financial_accounts(
    service: FinancialAccountService = Depends(get_financial_account_service),
):
    return service.get_all_accounts()


@router.get("/finance-accounts/{account_id}", response_model=FinancialAccountResponse)
def get_financial_account(
    account_id: int,
    service: FinancialAccountService = Depends(get_financial_account_service),
):
    try:
        return service.get_account_by_id(account_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post(
    "/finance-accounts",
    response_model=FinancialAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_financial_account(
    data: FinancialAccountCreate,
    service: FinancialAccountService = Depends(get_financial_account_service),
):
    try:
        return service.create_account(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/finance-accounts/{account_id}", response_model=FinancialAccountResponse)
def update_financial_account(
    account_id: int,
    data: FinancialAccountUpdate,
    service: FinancialAccountService = Depends(get_financial_account_service),
):
    try:
        return service.update_account(account_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/finance-accounts/{account_id}", response_model=FinancialAccountResponse)
def delete_financial_account(
    account_id: int,
    service: FinancialAccountService = Depends(get_financial_account_service),
):
    try:
        return service.delete_account(account_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.create_transaction(data)
    except ValueError as exc:
        message = str(exc)
        if "not found" in message:
            raise HTTPException(status_code=404, detail=message)
        raise HTTPException(status_code=400, detail=message)


@router.get("/transactions", response_model=List[TransactionResponse])
def get_transactions(
    user_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    amount: Optional[float] = None,
    transaction_date: Optional[date] = None,
    from_account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    service: TransactionService = Depends(get_transaction_service),
):
    if any(value is not None for value in (amount, transaction_date, from_account_id, category_id)):
        return service.find_transactions(
            user_id=user_id,
            amount=amount,
            transaction_date=transaction_date,
            from_account_id=from_account_id,
            category_id=category_id,
            limit=limit,
        )
    return service.get_transactions(user_id=user_id, limit=limit, offset=offset)


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    user_id: int,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.get_transaction_by_id(transaction_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    user_id: int,
    data: TransactionUpdate,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.update_transaction(transaction_id, user_id, data)
    except ValueError as exc:
        message = str(exc)
        raise HTTPException(status_code=404 if "not found" in message else 400, detail=message)


@router.delete("/transactions/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(
    transaction_id: int,
    user_id: int,
    service: TransactionService = Depends(get_transaction_service),
):
    try:
        return service.delete_transaction(transaction_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
