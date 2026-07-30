from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.modules.ai.adapters.repository import AIConversationRepository
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
from app.shared.database import get_db


router = APIRouter(prefix="/ai", tags=["AI","AI Orchestrator"])

@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def ai_chat(
    payload: AIChatRequest,
    db: Session = Depends(get_db),
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
        conversation_repository=AIConversationRepository(db),
    )

    return orchestrator.process(
        user_id=current_user.id,
        conversation_id=payload.conversation_id,
        message=payload.message,
    )
