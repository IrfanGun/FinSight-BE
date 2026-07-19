from fastapi import APIRouter, Depends

from app.modules.ai.application.orchestrator import FinanceOrchestrator
from app.modules.ai.application.schema import (
    AIChatRequest,
    AIChatResponse,
)
from app.modules.transactions.service_layer.transaction_service import (
    FinancialAccountService,
    TransactionCategoryService,
    TransactionService,
)
from app.modules.transactions.entrypoints.api import (
    get_transaction_service,
    get_transaction_category_service,
    get_financial_account_service,
)
from app.modules.users.entrypoints.api import get_current_user


router = APIRouter(prefix="/ai", tags=["AI","AI Orchestrator"])

@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def ai_chat(
    payload: AIChatRequest,
    transaction_service: TransactionService = Depends(
        get_transaction_service
    ),
    account_service: FinancialAccountService = Depends(
        get_financial_account_service
    ),
    category_service: TransactionCategoryService = Depends(
        get_transaction_category_service
    ),
    current_user=Depends(get_current_user),
):
    orchestrator = FinanceOrchestrator(
        transaction_service=transaction_service,
        account_service=account_service,
        category_service=category_service,
    )

    return orchestrator.process(
        user_id=current_user.id,
        message=payload.message,
    )
