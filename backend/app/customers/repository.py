"""Customers domain data access: CustomerRepository, CustomerNoteRepository."""

import uuid
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth.models import User
from app.customers.models import Customer, CustomerNote


class CustomerRepository:
    """Data access for Customer entities, always tenant-scoped."""

    @staticmethod
    async def create(session: AsyncSession, customer: Customer) -> Customer:
        """Insert a new customer row."""
        session.add(customer)
        await session.flush()
        return customer

    @staticmethod
    async def get_by_id(
        session: AsyncSession,
        customer_id: uuid.UUID,
        tenant_ids: list[uuid.UUID],
    ) -> Customer | None:
        """Fetch a single customer by ID, scoped to accessible tenants."""
        stmt = (
            select(Customer)
            .where(Customer.id == customer_id)
            .where(Customer.tenant_id.in_(tenant_ids))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(
        session: AsyncSession,
        email: str,
        tenant_ids: list[uuid.UUID],
    ) -> Customer | None:
        """Find a customer by email within the tenant scope."""
        if not email:
            return None
        stmt = (
            select(Customer)
            .where(Customer.email == email)
            .where(Customer.tenant_id.in_(tenant_ids))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_tenant(
        session: AsyncSession,
        tenant_ids: list[uuid.UUID],
        cursor: str | None,
        limit: int,
        search: str | None,
        sort_by: str,
        order: str,
        is_active: bool | None,
    ) -> tuple[list[Customer], bool]:
        """Cursor-paginated customer list with search and sort.

        Returns (items, has_more).
        """
        stmt = select(Customer).where(Customer.tenant_id.in_(tenant_ids))

        # ── Active filter ──────────────────────────────────
        if is_active is not None:
            stmt = stmt.where(Customer.is_active == is_active)

        # ── Search ─────────────────────────────────────────
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Customer.first_name.ilike(pattern),
                    Customer.last_name.ilike(pattern),
                    Customer.email.ilike(pattern),
                    Customer.phone.ilike(pattern),
                )
            )

        # ── Sorting ────────────────────────────────────────
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if order == "asc":
            stmt = stmt.order_by(sort_column.asc(), Customer.id.asc())
        else:
            stmt = stmt.order_by(sort_column.desc(), Customer.id.desc())

        # ── Cursor ─────────────────────────────────────────
        if cursor:
            try:
                cursor_id = uuid.UUID(cursor)
                stmt = stmt.where(Customer.id > cursor_id)
            except ValueError:
                pass  # Invalid cursor, ignore

        # Fetch limit+1 to detect has_more
        stmt = stmt.limit(limit + 1)
        result = await session.execute(stmt)
        rows = list(result.scalars().all())

        has_more = len(rows) > limit
        if has_more:
            rows = rows[:limit]

        return rows, has_more

    @staticmethod
    async def bulk_create(
        session: AsyncSession,
        customers: list[Customer],
    ) -> list[Customer]:
        """Insert multiple customers in a single flush."""
        session.add_all(customers)
        await session.flush()
        return customers


class CustomerNoteRepository:
    """Data access for CustomerNote entities."""

    @staticmethod
    async def create(session: AsyncSession, note: CustomerNote) -> CustomerNote:
        """Insert a new note."""
        session.add(note)
        await session.flush()
        return note

    @staticmethod
    async def list_by_customer(
        session: AsyncSession,
        customer_id: uuid.UUID,
        tenant_ids: list[uuid.UUID],
        cursor: str | None,
        limit: int,
    ) -> tuple[list[CustomerNote], bool]:
        """Cursor-paginated notes for a customer, newest first."""
        stmt = (
            select(CustomerNote)
            .options(joinedload(CustomerNote.customer))
            .where(CustomerNote.customer_id == customer_id)
            .where(CustomerNote.tenant_id.in_(tenant_ids))
            .order_by(CustomerNote.created_at.desc(), CustomerNote.id.desc())
        )

        if cursor:
            try:
                cursor_id = uuid.UUID(cursor)
                stmt = stmt.where(CustomerNote.id > cursor_id)
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
    ) -> int:
        """Count notes for a customer."""
        stmt = (
            select(func.count(CustomerNote.id))
            .where(CustomerNote.customer_id == customer_id)
            .where(CustomerNote.tenant_id.in_(tenant_ids))
        )
        result = await session.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def get_user_by_id(
        session: AsyncSession,
        user_id: uuid.UUID,
    ) -> User | None:
        """Fetch a user by ID for populating note author info."""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
