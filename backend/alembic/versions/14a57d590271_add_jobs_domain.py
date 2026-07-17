"""add_jobs_domain

Revision ID: 14a57d590271
Revises: 3c8d681e0f21
Create Date: 2026-07-17 16:10:27.735733
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '14a57d590271'
down_revision: Union[str, None] = '3c8d681e0f21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('jobs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('customer_id', sa.UUID(), nullable=False),
    sa.Column('appointment_id', sa.UUID(), nullable=True),
    sa.Column('assigned_to', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('estimated_hours', sa.Float(), nullable=True),
    sa.Column('actual_hours', sa.Float(), nullable=True),
    sa.Column('parts_cost', sa.Float(), nullable=True),
    sa.Column('labor_cost', sa.Float(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_assigned_to', 'jobs', ['assigned_to'], unique=False)
    op.create_index('idx_jobs_customer_id', 'jobs', ['customer_id'], unique=False)
    op.create_index('idx_jobs_tenant_id', 'jobs', ['tenant_id'], unique=False)
    op.create_index('idx_jobs_tenant_status', 'jobs', ['tenant_id', 'status'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_jobs_tenant_status', table_name='jobs')
    op.drop_index('idx_jobs_tenant_id', table_name='jobs')
    op.drop_index('idx_jobs_customer_id', table_name='jobs')
    op.drop_index('idx_jobs_assigned_to', table_name='jobs')
    op.drop_table('jobs')
