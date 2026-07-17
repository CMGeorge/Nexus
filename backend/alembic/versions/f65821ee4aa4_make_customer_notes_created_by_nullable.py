"""make_customer_notes_created_by_nullable

Revision ID: f65821ee4aa4
Revises: 39f9e2867723
Create Date: 2026-07-17 13:48:58.466207
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f65821ee4aa4'
down_revision: Union[str, None] = '39f9e2867723'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('customer_notes', 'created_by',
                    existing_type=sa.UUID(),
                    nullable=True)


def downgrade() -> None:
    op.alter_column('customer_notes', 'created_by',
                    existing_type=sa.UUID(),
                    nullable=False)
