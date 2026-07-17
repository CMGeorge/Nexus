"""Jobs domain REST API router."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_current_tenant_id, require_role
from app.core.tenant import get_accessible_tenant_ids
from app.jobs.deps import get_job_service
from app.jobs.schemas import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobUpdate,
    MessageResponse,
)
from app.jobs.service import JobService

router = APIRouter()


async def _resolve_tenant_ids(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> list[uuid.UUID]:
    return await get_accessible_tenant_ids(tenant_id, session)


TenantIdsDep = Depends(_resolve_tenant_ids)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: dict[str, Any] = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    """Create a new job/work order. Requires: Employee, Manager, or Admin."""
    return await service.create(tenant_id, data)


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    customer_id: uuid.UUID | None = Query(None),
    assigned_to: uuid.UUID | None = Query(None),
) -> JobListResponse:
    """List jobs with cursor pagination and filters."""
    return await service.list_jobs(tenant_ids, cursor, limit, status, customer_id, assigned_to)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    """Get a single job by ID."""
    return await service.get(tenant_ids, job_id)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    data: JobUpdate,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: JobService = Depends(get_job_service),
) -> JobResponse:
    """Partially update a job."""
    return await service.update(tenant_ids, job_id, data)


@router.post("/{job_id}/cancel", response_model=MessageResponse)
async def cancel_job(
    job_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(require_role("Admin", "Manager")),
    service: JobService = Depends(get_job_service),
) -> MessageResponse:
    """Cancel a job. Requires: Manager or Admin."""
    return await service.cancel(tenant_ids, job_id)