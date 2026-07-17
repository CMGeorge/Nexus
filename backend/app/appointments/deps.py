"""Appointments domain FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.appointments.service import AppointmentService


async def get_appointment_service(
    session: AsyncSession = Depends(get_session),
) -> AppointmentService:
    """Dependency that provides an AppointmentService instance."""
    return AppointmentService(session)