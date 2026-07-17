# app/modules/ai/adapters/orm.py

from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.database import Base


class Intent(Base):
    __tablename__ = "intents"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    code = Column(String(100), nullable=False, unique=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=True)
    route = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    examples = relationship(
        "IntentExample",
        back_populates="intent",
        cascade="all, delete-orphan",
    )


class IntentExample(Base):
    __tablename__ = "intent_examples"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    intent_id = Column(BigInteger, ForeignKey("intents.id", ondelete="CASCADE"))
    example_text = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=True)
    created_by = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    intent = relationship("Intent", back_populates="examples")


class AIIntentLog(Base):
    __tablename__ = "ai_intent_logs"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    query = Column(Text, nullable=False)
    predicted_intent = Column(String(100), nullable=True)
    predicted_route = Column(String(30), nullable=True)
    matched_example = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    distance_score = Column(Float, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    corrected_intent = Column(String(100), nullable=True)
    reviewed_by = Column(BigInteger, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())