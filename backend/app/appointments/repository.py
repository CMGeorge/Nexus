"""Appointments domain data access."""

import uuid

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.models import Appointment


class AppointmentRepository:
    """Data access for Appointment entities, always tenant-scoped."""

    @staticmethod
    async def create(session: AsyncSession, appointment: Appointment) -> Appointment:
        session.add(appointment)
        await session.flush()
        return appointment

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        appointment_id: uuid.UUID,
        tenant_ids: list[uuid.UUID],
    ) -> Appointment | None:
        stmt = (
            select(Appointment)
            .where(Appointment.id == appointment_id)
            .where(Appointment.tenant_id.in_(tenant_ids))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        session: AsyncSession,
        tenant_ids: list[uuid.UUID],
        cursor: str | None,
        limit: int,
        status: str | None,
        customer_id: uuid.UUID | None,
        assigned_to: uuid.UUID | None,
        from_date: str | None,
        to_date: str | None,
    ) -> tuple[list[Appointment], bool]:
        """Cursor-paginated appointment list with filters.

        Returns (items, has_more).
        """
        stmt = select(Appointment).where(Appointment.tenant_id.in_(tenant_ids))

        if status:
            stmt = stmt.where(Appointment.status == status)
        if customer_id:
            stmt = stmt.where(Appointment.customer_id == customer_id)
        if assigned_to:
            stmt = stmt.where(Appointment.assigned_to == assigned_to)
        if from_date:
            stmt = stmt.where(Appointment.scheduled_at >= from_date)
        if to_date:
            stmt = stmt.where(Appointment.scheduled_at <= to_date)

        stmt = stmt.order_by(Appointment.scheduled_at.asc(), Appointment.id.asc())

        if cursor:
            try:
                cursor_id = uuid.UUID(cursor)
                stmt = stmt.where(Appointment.id > cursor_id)
            except ValueError:
                pass

        stmt = stmt.limit(limit + 1)
        result = await session.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more

    @staticmethod
    async def count_by_customer(
        session: AsyncSession,
        customer_id: uuid.UUID,
        tenant_ids: list[uuid.UUID],
        upcoming_only: bool = False,
    ) -> int:
        """Count appointments for a customer (used by history endpoint)."""
        from sqlalchemy import func as sqlfunc

        stmt = (
            select(sqlfunc.count(Appointment.id))
            .where(Appointment.customer_id == customer_id)
            .where(Appointment.tenant_id.in_(tenant_ids))
        )
        if upcoming_only:
            stmt = stmt.where(Appointment.status.in_(["confirmed", "in_progress"]))
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_recent_by_customer(
        session: AsyncSession,
        customer_id: uuid.UUID,
        tenant_ids: list[uuid.UUID],
        limit: int = 5,
    ) -> list[Appointment]:
        """Get most recent appointments for a customer."""
        stmt = (
            select(Appointment)
            .where(Appointment.customer_id == customer_id)
            .where(Appointment.tenant_id.in_(tenant_ids))
            .order_by(Appointment.scheduled_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())