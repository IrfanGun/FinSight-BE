from fastapi import APIRouter, Depends, HTTPException, Query
from math import ceil
from sqlalchemy.orm import Session

from app.modules.ai.adapters.repository import AIConversationRepository
from app.modules.ai.application.orchestrator import FinanceOrchestrator
from app.modules.ai.application.schema import (
    AIChatRequest,
    AIChatResponse,
    AIConversationResponse,
    AIMessageResponse,
    AIPaginatedMessagesResponse,
    AIPaginatedConversationsResponse,
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


@router.get(
    "/conversations",
    response_model=AIPaginatedConversationsResponse,
)
def get_conversations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    total, conversations = AIConversationRepository(db).get_conversations_page(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    return {
        "items": conversations,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=AIPaginatedMessagesResponse,
)
def get_conversation_messages(
    conversation_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = AIConversationRepository(db).get_messages_page(
        conversation_id=conversation_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    total, messages = result
    return {
        "items": [
            {
                "id": item.id,
                "role": item.role,
                "message": item.message,
                "intent": item.intent,
                "metadata": item.metadata_json,
                "created_at": item.created_at,
            }
            for item in messages
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": ceil(total / page_size) if total else 0,
    }


@router.get(
    "/conversations/{conversation_id}",
    response_model=AIConversationResponse,
)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = AIConversationRepository(db).get_by_id_with_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation tidak ditemukan")

    conversation, messages = result
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [
            {
                "id": item.id,
                "role": item.role,
                "message": item.message,
                "intent": item.intent,
                "metadata": item.metadata_json,
                "created_at": item.created_at,
            }
            for item in messages
        ],
    }

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
