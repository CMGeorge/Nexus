"""Customers domain FastAPI dependencies."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.customers.service import CustomerService


async def get_customer_service(
    session: AsyncSession = Depends(get_session),
) -> CustomerService:
    """Dependency that provides a CustomerService instance."""
    return CustomerService(session)
