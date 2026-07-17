"""Appointments domain ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Appointment(Base):
    """Scheduled appointment for a customer.

    Status lifecycle: confirmed → in_progress → completed
                    confirmed → cancelled

    Multi-tenant: scoped by tenant_id.
    """

    __tablename__ = "appointments"
    __table_args__ = (
        Index("idx_appointments_tenant_id", "tenant_id"),
        Index("idx_appointments_customer_id", "customer_id"),
        Index("idx_appointments_assigned_to", "assigned_to"),
        Index("idx_appointments_tenant_status", "tenant_id", "status"),
        Index("idx_appointments_tenant_scheduled", "tenant_id", "scheduled_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
    )
    duration_minutes: Mapped[int] = mapped_column(default=60, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="confirmed", nullable=False,
    )  # confirmed | in_progress | completed | cancelled
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Appointment(id={self.id}, status={self.status})>"