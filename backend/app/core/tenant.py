"""Tenant model + hierarchical multi-tenancy resolution.

Implements ADR-0010: Institution → Branch hierarchy.
- Institution (parent_id IS NULL): can see all branches
- Branch (parent_id IS NOT NULL): can only see its own data
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Tenant(Base):
    """Hierarchical tenant: institutions (parent_id=NULL) have branches."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    subdomain: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    @property
    def is_institution(self) -> bool:
        return self.parent_id is None

    @property
    def is_branch(self) -> bool:
        return self.parent_id is not None


async def get_accessible_tenant_ids(
    tenant_id: uuid.UUID,
    session: AsyncSession,
) -> list[uuid.UUID]:
    """Return all tenant IDs the current user can access.

    - Institution-level: returns [institution_id] + [all branch IDs]
    - Branch-level: returns [branch_id] only

    This is designed to be used in repository queries as:
        WHERE tenant_id = ANY(:accessible_tenant_ids)
    """
    stmt = select(Tenant).where(Tenant.id == tenant_id)
    result = await session.execute(stmt)
    tenant = result.scalar_one_or_none()

    if tenant is None:
        return [tenant_id]  # Fallback: just the provided ID

    if tenant.is_institution:
        # Institution user — include all child branches
        children_stmt = select(Tenant.id).where(Tenant.parent_id == tenant_id)
        children_result = await session.execute(children_stmt)
        child_ids = [row[0] for row in children_result]
        return [tenant_id] + child_ids
    else:
        # Branch user — only their branch
        return [tenant_id]


def is_tenant_hierarchy_supported() -> bool:
    """Feature flag: hierarchical tenants are enabled (ADR-0010)."""
    return True
