"""Appointments domain REST API router."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_current_tenant_id, require_role
from app.core.tenant import get_accessible_tenant_ids
from app.appointments.deps import get_appointment_service
from app.appointments.schemas import (
    AppointmentCreate,
    AppointmentListResponse,
    AppointmentResponse,
    AppointmentUpdate,
    MessageResponse,
)
from app.appointments.service import AppointmentService

router = APIRouter()


async def _resolve_tenant_ids(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> list[uuid.UUID]:
    return await get_accessible_tenant_ids(tenant_id, session)


TenantIdsDep = Depends(_resolve_tenant_ids)


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    """Create a new appointment. Requires: Employee, Manager, or Admin."""
    return await service.create(tenant_id, data)


@router.get("/", response_model=AppointmentListResponse)
async def list_appointments(
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None, description="Filter: confirmed, in_progress, completed, cancelled"),
    customer_id: uuid.UUID | None = Query(None),
    assigned_to: uuid.UUID | None = Query(None),
    from_date: str | None = Query(None, description="ISO 8601 start date"),
    to_date: str | None = Query(None, description="ISO 8601 end date"),
) -> AppointmentListResponse:
    """List appointments with cursor pagination and filters."""
    return await service.list_appointments(
        tenant_ids, cursor, limit, status, customer_id, assigned_to, from_date, to_date,
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    """Get a single appointment by ID."""
    return await service.get(tenant_ids, appointment_id)


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: uuid.UUID,
    data: AppointmentUpdate,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AppointmentService = Depends(get_appointment_service),
) -> AppointmentResponse:
    """Partially update an appointment."""
    return await service.update(tenant_ids, appointment_id, data)


@router.post("/{appointment_id}/cancel", response_model=MessageResponse)
async def cancel_appointment(
    appointment_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(require_role("Admin", "Manager")),
    service: AppointmentService = Depends(get_appointment_service),
) -> MessageResponse:
    """Cancel an appointment. Requires: Manager or Admin."""
    return await service.cancel(tenant_ids, appointment_id)