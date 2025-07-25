"""feat: add information of planning publish time and displayed publish time of article

Revision ID: 6a452d282ffb
Revises: 10bdf9662be6
Create Date: 2025-07-17 12:36:01.126832

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "6a452d282ffb"
down_revision: str | Sequence[str] | None = "10bdf9662be6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "article",
        sa.Column(
            "published_at", postgresql.TIMESTAMP(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "article",
        sa.Column(
            "scheduled_publish_time",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("article", "scheduled_publish_time")
    op.drop_column("article", "published_at")
    # ### end Alembic commands ###
