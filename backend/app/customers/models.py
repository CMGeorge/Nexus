"""Customers domain ORM models: Customer, CustomerNote."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Customer(Base):
    """End-customer of a tenant's business.

    These are NOT platform users — they are the tenant's own client base.
    Platform users (who log in) are managed by the auth domain.

    Multi-tenant: scoped by tenant_id. Hierarchical tenants (ADR-0010)
    query via tenant_id = ANY(:accessible_tenant_ids).

    Soft-delete: is_active=False preserves referential integrity.
    """

    __tablename__ = "customers"
    __table_args__ = (
        Index("idx_customers_tenant_id", "tenant_id"),
        Index("idx_customers_tenant_name", "tenant_id", "last_name", "first_name"),
        Index("idx_customers_tenant_email", "tenant_id", "email"),
        Index("idx_customers_tenant_phone", "tenant_id", "phone"),
        Index("idx_customers_tenant_active", "tenant_id", "is_active"),
        UniqueConstraint(
            "tenant_id", "email",
            name="uq_customers_tenant_email",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address_line1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address_line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    county: Mapped[str | None] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country: Mapped[str | None] = mapped_column(
        String(2), nullable=True, default="RO",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    # ── Relationships ──────────────────────────────────────────
    notes: Mapped[list["CustomerNote"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, name={self.first_name} {self.last_name})>"


class CustomerNote(Base):
    """Free-text note attached to a customer profile.

    Notes are written by platform users (employees/managers) and are
    tenant-scoped for multi-tenant isolation.
    """

    __tablename__ = "customer_notes"
    __table_args__ = (
        Index("idx_customer_notes_customer", "customer_id"),
        Index("idx_customer_notes_tenant", "tenant_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    # ── Relationships ──────────────────────────────────────────
    customer: Mapped["Customer"] = relationship(back_populates="notes")

    def __repr__(self) -> str:
        return f"<CustomerNote(id={self.id}, customer_id={self.customer_id})>"