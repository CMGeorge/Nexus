"""Jobs domain FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.jobs.service import JobService


async def get_job_service(
    session: AsyncSession = Depends(get_session),
) -> JobService:
    return JobService(session)