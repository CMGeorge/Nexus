"""Jobs domain data access."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.models import Job


class JobRepository:
    """Data access for Job entities, always tenant-scoped."""

    @staticmethod
    async def create(session: AsyncSession, job: Job) -> Job:
        session.add(job)
        await session.flush()
        return job

    @staticmethod
    async def get_by_id(
        session: AsyncSession, job_id: uuid.UUID, tenant_ids: list[uuid.UUID],
    ) -> Job | None:
        stmt = select(Job).where(Job.id == job_id).where(Job.tenant_id.in_(tenant_ids))
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
    ) -> tuple[list[Job], bool]:
        stmt = select(Job).where(Job.tenant_id.in_(tenant_ids))
        if status:
            stmt = stmt.where(Job.status == status)
        if customer_id:
            stmt = stmt.where(Job.customer_id == customer_id)
        if assigned_to:
            stmt = stmt.where(Job.assigned_to == assigned_to)

        stmt = stmt.order_by(Job.created_at.desc(), Job.id.desc())

        if cursor:
            try:
                cursor_id = uuid.UUID(cursor)
                stmt = stmt.where(Job.id > cursor_id)
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
        session: AsyncSession, customer_id: uuid.UUID, tenant_ids: list[uuid.UUID],
        active_only: bool = False,
    ) -> int:
        stmt = (
            select(func.count(Job.id))
            .where(Job.customer_id == customer_id)
            .where(Job.tenant_id.in_(tenant_ids))
        )
        if active_only:
            stmt = stmt.where(Job.status.in_(["pending", "in_progress"]))
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_recent_by_customer(
        session: AsyncSession, customer_id: uuid.UUID, tenant_ids: list[uuid.UUID],
        limit: int = 5,
    ) -> list[Job]:
        stmt = (
            select(Job)
            .where(Job.customer_id == customer_id)
            .where(Job.tenant_id.in_(tenant_ids))
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())