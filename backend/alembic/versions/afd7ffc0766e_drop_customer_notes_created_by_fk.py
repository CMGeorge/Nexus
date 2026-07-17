"""drop_customer_notes_created_by_fk

Revision ID: afd7ffc0766e
Revises: f65821ee4aa4
Create Date: 2026-07-17 13:50:00.469780
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afd7ffc0766e'
down_revision: Union[str, None] = 'f65821ee4aa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('customer_notes_created_by_fkey', 'customer_notes', type_='foreignkey')


def downgrade() -> None:
    op.create_foreign_key('customer_notes_created_by_fkey', 'customer_notes', 'users', ['created_by'], ['id'])
