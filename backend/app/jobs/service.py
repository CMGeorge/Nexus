"""Jobs domain service: business logic."""

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.models import Job
from app.jobs.repository import JobRepository
from app.jobs.schemas import (
    JobCreate,
    JobListResponse,
    JobResponse,
    JobSummary,
    JobUpdate,
    CursorMeta,
    MessageResponse,
)


class JobService:
    """Business logic for job/work-order management."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = JobRepository()

    async def create(self, tenant_id: uuid.UUID, data: JobCreate) -> JobResponse:
        job = Job(
            tenant_id=tenant_id,
            customer_id=data.customer_id,
            appointment_id=data.appointment_id,
            assigned_to=data.assigned_to,
            title=data.title,
            description=data.description,
            estimated_hours=data.estimated_hours,
            notes=data.notes,
        )
        job = await self.repo.create(self.session, job)
        return JobResponse.model_validate(job)

    async def get(self, tenant_ids: list[uuid.UUID], job_id: uuid.UUID) -> JobResponse:
        job = await self.repo.get_by_id(self.session, job_id, tenant_ids)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        return JobResponse.model_validate(job)

    async def list_jobs(
        self, tenant_ids: list[uuid.UUID], cursor: str | None, limit: int,
        status_filter: str | None, customer_id: uuid.UUID | None, assigned_to: uuid.UUID | None,
    ) -> JobListResponse:
        jobs, has_more = await self.repo.list_by_tenant(
            self.session, tenant_ids, cursor, limit, status_filter, customer_id, assigned_to,
        )
        next_cursor = str(jobs[-1].id) if has_more and jobs else None
        return JobListResponse(
            data=[JobSummary.model_validate(j) for j in jobs],
            cursor=CursorMeta(next=next_cursor, has_more=has_more),
        )

    async def update(
        self, tenant_ids: list[uuid.UUID], job_id: uuid.UUID, data: JobUpdate,
    ) -> JobResponse:
        job = await self.repo.get_by_id(self.session, job_id, tenant_ids)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job, field, value)

        # Auto-set completed_at when status changes to completed/invoiced
        if "status" in update_data and update_data["status"] in ("completed", "invoiced"):
            job.completed_at = datetime.now(UTC)

        await self.session.flush()
        return JobResponse.model_validate(job)

    async def cancel(self, tenant_ids: list[uuid.UUID], job_id: uuid.UUID) -> MessageResponse:
        job = await self.repo.get_by_id(self.session, job_id, tenant_ids)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
        job.status = "cancelled"
        job.is_active = False
        await self.session.flush()
        return MessageResponse(message="Job cancelled.")

    async def get_stats_by_customer(
        self, tenant_ids: list[uuid.UUID], customer_id: uuid.UUID,
    ) -> dict:
        """Aggregated stats for customer history endpoint."""
        total = await self.repo.count_by_customer(self.session, customer_id, tenant_ids)
        active = await self.repo.count_by_customer(self.session, customer_id, tenant_ids, active_only=True)
        recent = await self.repo.get_recent_by_customer(self.session, customer_id, tenant_ids, limit=5)

        return {
            "total": total,
            "active": active,
            "recent": [
                {"id": str(j.id), "title": j.title, "status": j.status}
                for j in recent
            ],
        }