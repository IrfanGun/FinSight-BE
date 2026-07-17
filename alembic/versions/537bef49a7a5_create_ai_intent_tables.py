"""create_ai_intent_tables

Revision ID: 537bef49a7a5
Revises: 20260613_000001
Create Date: 2026-06-15 14:34:19.515583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision: str = '537bef49a7a5'
down_revision: Union[str, Sequence[str], None] = '20260613_000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():

    # =====================================================
    # INTENTS
    # =====================================================

    op.create_table(
        "intents",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("route", sa.String(30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),

        sa.UniqueConstraint(
            "code",
            name="uq_intents_code"
        ),
    )

    op.create_index(
        "ix_intents_code",
        "intents",
        ["code"]
    )

    # =====================================================
    # INTENT EXAMPLES
    # =====================================================

    op.create_table(
        "intent_examples",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),

        sa.Column(
            "intent_id",
            sa.BigInteger(),
            nullable=False
        ),

        sa.Column(
            "example_text",
            sa.Text(),
            nullable=False
        ),

        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true")
        ),

        sa.Column(
            "created_by",
            sa.BigInteger(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),

        sa.ForeignKeyConstraint(
            ["intent_id"],
            ["intents.id"],
            name="fk_intent_examples_intent_id",
            ondelete="CASCADE"
        )
    )

    op.create_index(
        "ix_intent_examples_intent_id",
        "intent_examples",
        ["intent_id"]
    )

    # =====================================================
    # AI INTENT LOGS
    # =====================================================

    op.create_table(
        "ai_intent_logs",

        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True
        ),

        sa.Column(
            "user_id",
            sa.BigInteger(),
            nullable=True
        ),

        sa.Column(
            "query",
            sa.Text(),
            nullable=False
        ),

        # Prediction
        sa.Column(
            "predicted_intent",
            sa.String(100),
            nullable=True
        ),

        sa.Column(
            "predicted_route",
            sa.String(30),
            nullable=True
        ),

        sa.Column(
            "matched_example",
            sa.Text(),
            nullable=True
        ),

        # Confidence
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=True
        ),

        sa.Column(
            "distance_score",
            sa.Float(),
            nullable=True
        ),

        # Human Evaluation
        sa.Column(
            "is_correct",
            sa.Boolean(),
            nullable=True
        ),

        sa.Column(
            "corrected_intent",
            sa.String(100),
            nullable=True
        ),

        sa.Column(
            "reviewed_by",
            sa.BigInteger(),
            nullable=True
        ),

        sa.Column(
            "reviewed_at",
            sa.DateTime(),
            nullable=True
        ),

        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        ),
    )

    op.create_index(
        "ix_ai_intent_logs_created_at",
        "ai_intent_logs",
        ["created_at"]
    )

    op.create_index(
        "ix_ai_intent_logs_predicted_intent",
        "ai_intent_logs",
        ["predicted_intent"]
    )

    op.create_index(
        "ix_ai_intent_logs_confidence_score",
        "ai_intent_logs",
        ["confidence_score"]
    )


def downgrade():

    op.drop_index(
        "ix_ai_intent_logs_confidence_score",
        table_name="ai_intent_logs"
    )

    op.drop_index(
        "ix_ai_intent_logs_predicted_intent",
        table_name="ai_intent_logs"
    )

    op.drop_index(
        "ix_ai_intent_logs_created_at",
        table_name="ai_intent_logs"
    )

    op.drop_table("ai_intent_logs")

    op.drop_index(
        "ix_intent_examples_intent_id",
        table_name="intent_examples"
    )

    op.drop_table("intent_examples")

    op.drop_index(
        "ix_intents_code",
        table_name="intents"
    )

    op.drop_table("intents")