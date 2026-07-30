# app/modules/ai/adapters/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime

from app.modules.ai.adapters.orm import Intent, IntentExample, AIIntentLog
from app.modules.transactions.adapters.orm import AIConversationORM, AIMessageORM


class AIConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: int, conversation_id: int | None = None):
        conversation = None
        if conversation_id is not None:
            conversation = (
                self.db.query(AIConversationORM)
                .filter(AIConversationORM.id == conversation_id,
                        AIConversationORM.user_id == user_id)
                .first()
            )
        if conversation is None:
            conversation = AIConversationORM(user_id=user_id)
            self.db.add(conversation)
            self.db.flush()
        return conversation

    def add_message(self, *, conversation_id: int, user_id: int,
                    role: str, message: str, intent: str | None = None,
                    metadata: dict | None = None):
        row = AIMessageORM(
            conversation_id=conversation_id, user_id=user_id, role=role,
            message=message, intent=intent, metadata_json=metadata,
        )
        self.db.add(row)
        self.db.flush()
        return row

    def get_recent_messages(self, *, conversation_id: int, user_id: int,
                            limit: int = 12):
        rows = (
            self.db.query(AIMessageORM)
            .filter(AIMessageORM.conversation_id == conversation_id,
                   AIMessageORM.user_id == user_id)
            .order_by(AIMessageORM.created_at.desc(), AIMessageORM.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(rows))

    def commit(self):
        self.db.commit()


class IntentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_intent_by_code(self, code: str):
        return (
            self.db.query(Intent)
            .filter(Intent.code == code)
            .first()
        )

    def create_intent(
        self,
        code: str,
        name: str,
        route: str,
        category: str | None = None,
        description: str | None = None,
    ):
        intent = Intent(
            code=code,
            name=name,
            route=route,
            category=category,
            description=description,
        )

        self.db.add(intent)
        self.db.flush()

        return intent

    def create_intent_example(
        self,
        intent_id: int,
        example_text: str,
        created_by: int | None = None,
        is_verified: bool = True,
    ):
        example = IntentExample(
            intent_id=intent_id,
            example_text=example_text,
            created_by=created_by,
            is_verified=is_verified,
        )

        self.db.add(example)
        self.db.flush()

        return example

    def example_exists(self, example_text: str) -> bool:
        return (
            self.db.query(IntentExample)
            .filter(IntentExample.example_text == example_text)
            .first()
            is not None
        )

    def get_verified_examples(self):
        return (
            self.db.query(IntentExample)
            .join(Intent)
            .filter(Intent.is_active == True)
            .filter(IntentExample.is_verified == True)
            .all()
        )

    def create_log(
        self,
        user_id: int | None,
        query: str,
        predicted_intent: str | None,
        predicted_route: str | None,
        matched_example: str | None,
        confidence_score: float | None,
        distance_score: float | None,
    ):
        log = AIIntentLog(
            user_id=user_id,
            query=query,
            predicted_intent=predicted_intent,
            predicted_route=predicted_route,
            matched_example=matched_example,
            confidence_score=confidence_score,
            distance_score=distance_score,
        )
        self.db.add(log)
        self.db.flush()
        return log

    def get_log_by_id(self, log_id: int):
        return (
            self.db.query(AIIntentLog)
            .filter(AIIntentLog.id == log_id)
            .first()
        )

    def correct_log(
        self,
        log: AIIntentLog,
        corrected_intent: str,
        reviewed_by: int | None = None,
    ):
        log.corrected_intent = corrected_intent
        log.is_correct = log.predicted_intent == corrected_intent
        log.reviewed_by = reviewed_by
        log.reviewed_at = datetime.utcnow()
        self.db.flush()
        return log

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
