"""Appointments domain service: business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.appointments.models import Appointment
from app.appointments.repository import AppointmentRepository
from app.appointments.schemas import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentSummary,
    AppointmentUpdate,
    CursorMeta,
    MessageResponse,
)


class AppointmentService:
    """Business logic for appointment management. Always tenant-scoped."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = AppointmentRepository()

    async def create(
        self, tenant_id: uuid.UUID, data: AppointmentCreate,
    ) -> AppointmentResponse:
        appointment = Appointment(
            tenant_id=tenant_id,
            customer_id=data.customer_id,
            assigned_to=data.assigned_to,
            title=data.title,
            description=data.description,
            scheduled_at=data.scheduled_at,
            duration_minutes=data.duration_minutes,
            notes=data.notes,
        )
        appointment = await self.repo.create(self.session, appointment)
        return AppointmentResponse.model_validate(appointment)

    async def get(
        self, tenant_ids: list[uuid.UUID], appointment_id: uuid.UUID,
    ) -> AppointmentResponse:
        appointment = await self.repo.get_by_id(self.session, appointment_id, tenant_ids)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
        return AppointmentResponse.model_validate(appointment)

    async def list_appointments(
        self,
        tenant_ids: list[uuid.UUID],
        cursor: str | None,
        limit: int,
        status_filter: str | None,
        customer_id: uuid.UUID | None,
        assigned_to: uuid.UUID | None,
        from_date: str | None,
        to_date: str | None,
    ) -> AppointmentListResponse:
        appointments, has_more = await self.repo.list_by_tenant(
            self.session, tenant_ids, cursor, limit,
            status_filter, customer_id, assigned_to, from_date, to_date,
        )
        next_cursor = str(appointments[-1].id) if has_more and appointments else None
        return AppointmentListResponse(
            data=[AppointmentSummary.model_validate(a) for a in appointments],
            cursor=CursorMeta(next=next_cursor, has_more=has_more),
        )

    async def update(
        self, tenant_ids: list[uuid.UUID], appointment_id: uuid.UUID, data: AppointmentUpdate,
    ) -> AppointmentResponse:
        appointment = await self.repo.get_by_id(self.session, appointment_id, tenant_ids)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(appointment, field, value)

        await self.session.flush()
        return AppointmentResponse.model_validate(appointment)

    async def cancel(
        self, tenant_ids: list[uuid.UUID], appointment_id: uuid.UUID,
    ) -> MessageResponse:
        appointment = await self.repo.get_by_id(self.session, appointment_id, tenant_ids)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")

        appointment.status = "cancelled"
        appointment.is_active = False
        await self.session.flush()
        return MessageResponse(message="Appointment cancelled.")

    async def get_stats_by_customer(
        self, tenant_ids: list[uuid.UUID], customer_id: uuid.UUID,
    ) -> dict:
        """Aggregated stats for customer history endpoint."""
        total = await self.repo.count_by_customer(self.session, customer_id, tenant_ids)
        upcoming = await self.repo.count_by_customer(self.session, customer_id, tenant_ids, upcoming_only=True)
        recent = await self.repo.get_recent_by_customer(self.session, customer_id, tenant_ids, limit=5)

        return {
            "total": total,
            "upcoming": upcoming,
            "recent": [
                {
                    "id": str(a.id),
                    "title": a.title,
                    "scheduled_at": a.scheduled_at.isoformat(),
                    "status": a.status,
                }
                for a in recent
            ],
        }