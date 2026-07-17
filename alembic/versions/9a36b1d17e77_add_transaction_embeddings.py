"""add transaction embeddings"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260613_000001"
down_revision: Union[str, None] = "20260606_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass