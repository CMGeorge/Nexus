"""Customers domain service: business logic for customer management."""

import csv
import io
import uuid
from datetime import datetime, UTC

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.customers.models import Customer, CustomerNote
from app.customers.repository import CustomerNoteRepository, CustomerRepository
from app.customers.schemas import (
    CsvImportError,
    CsvImportResponse,
    CustomerCreate,
    CustomerHistorySummary,
    CustomerListResponse,
    CustomerNoteCreate,
    CustomerNoteListResponse,
    CustomerNoteResponse,
    CustomerResponse,
    CustomerSummary,
    CursorMeta,
    CustomerUpdate,
    MessageResponse,
)


class CustomerService:
    """Business logic for customer management.

    All operations are tenant-scoped. The tenant context (list of accessible
    tenant IDs for hierarchical support) is passed explicitly.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.customer_repo = CustomerRepository()
        self.note_repo = CustomerNoteRepository()

    # ── Create ─────────────────────────────────────────────────

    async def create(
        self,
        tenant_id: uuid.UUID,
        data: CustomerCreate,
    ) -> CustomerResponse:
        """Create a new customer for the tenant."""
        # Check duplicate email within tenant
        if data.email:
            existing = await self.customer_repo.get_by_email(
                self.session, data.email, [tenant_id],
            )
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A customer with this email already exists in your company.",
                )

        customer = Customer(
            tenant_id=tenant_id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            address_line1=data.address_line1,
            address_line2=data.address_line2,
            city=data.city,
            county=data.county,
            postal_code=data.postal_code,
            country=data.country or "RO",
        )
        customer = await self.customer_repo.create(self.session, customer)
        return CustomerResponse.model_validate(customer)

    # ── Read ───────────────────────────────────────────────────

    async def get(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
    ) -> CustomerResponse:
        """Get a single customer by ID, scoped to accessible tenants."""
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )
        return CustomerResponse.model_validate(customer)

    async def list_customers(
        self,
        tenant_ids: list[uuid.UUID],
        cursor: str | None,
        limit: int,
        search: str | None,
        sort_by: str,
        order: str,
        is_active: bool | None,
    ) -> CustomerListResponse:
        """List customers with cursor-based pagination."""
        valid_sort_fields = {"first_name", "last_name", "email", "created_at"}
        if sort_by not in valid_sort_fields:
            sort_by = "created_at"

        customers, has_more = await self.customer_repo.list_by_tenant(
            self.session, tenant_ids, cursor, limit, search, sort_by, order, is_active,
        )

        next_cursor = None
        if has_more and customers:
            next_cursor = str(customers[-1].id)

        return CustomerListResponse(
            data=[CustomerSummary.model_validate(c) for c in customers],
            cursor=CursorMeta(next=next_cursor, has_more=has_more),
        )

    # ── Update ─────────────────────────────────────────────────

    async def update(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
        data: CustomerUpdate,
    ) -> CustomerResponse:
        """Partially update a customer (PATCH semantics)."""
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        # Check duplicate email if changing
        if data.email and data.email != customer.email:
            existing = await self.customer_repo.get_by_email(
                self.session, data.email, tenant_ids,
            )
            if existing and existing.id != customer_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A customer with this email already exists in your company.",
                )

        # Apply partial updates
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        customer.updated_at = datetime.now(UTC)  # type: ignore[assignment]
        await self.session.flush()
        return CustomerResponse.model_validate(customer)

    # ── Deactivate (Soft Delete) ───────────────────────────────

    async def deactivate(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
    ) -> MessageResponse:
        """Soft-delete a customer by setting is_active=False."""
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        customer.is_active = False
        customer.updated_at = datetime.now(UTC)  # type: ignore[assignment]
        await self.session.flush()
        return MessageResponse(message="Customer has been deactivated.")

    # ── Notes ──────────────────────────────────────────────────

    async def add_note(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
        user_id: uuid.UUID,
        data: CustomerNoteCreate,
    ) -> CustomerNoteResponse:
        """Add a note to a customer profile."""
        # Verify customer exists and is accessible
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        note = CustomerNote(
            customer_id=customer_id,
            tenant_id=customer.tenant_id,
            content=data.content,
            created_by=user_id,
        )
        note = await self.note_repo.create(self.session, note)

        # Look up the author's real name from the users table
        author = await self.note_repo.get_user_by_id(self.session, user_id)
        author_info: dict = {"id": user_id, "first_name": None, "last_name": None}
        if author is not None:
            author_info = {
                "id": author.id,
                "first_name": author.first_name,
                "last_name": author.last_name,
            }

        return CustomerNoteResponse(
            id=note.id,
            customer_id=note.customer_id,
            content=note.content,
            created_by=author_info,  # type: ignore[arg-type]
            created_at=note.created_at,
            updated_at=note.updated_at,
        )

    async def list_notes(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
        cursor: str | None,
        limit: int,
    ) -> CustomerNoteListResponse:
        """List notes for a customer, newest first."""
        # Verify customer exists
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        notes, has_more = await self.note_repo.list_by_customer(
            self.session, customer_id, tenant_ids, cursor, limit,
        )

        # Collect unique author IDs and fetch their names
        author_ids = {n.created_by for n in notes if n.created_by}
        author_map: dict[uuid.UUID, dict] = {}
        for aid in author_ids:
            user = await self.note_repo.get_user_by_id(self.session, aid)
            if user is not None:
                author_map[aid] = {"id": user.id, "first_name": user.first_name, "last_name": user.last_name}
            else:
                author_map[aid] = {"id": aid, "first_name": None, "last_name": None}

        next_cursor = None
        if has_more and notes:
            next_cursor = str(notes[-1].id)

        return CustomerNoteListResponse(
            data=[
                CustomerNoteResponse(
                    id=n.id,
                    customer_id=n.customer_id,
                    content=n.content,
                    created_by=author_map.get(n.created_by, {"id": n.created_by, "first_name": None, "last_name": None}),  # type: ignore[arg-type]
                    created_at=n.created_at,
                    updated_at=n.updated_at,
                )
                for n in notes
            ],
            cursor=CursorMeta(next=next_cursor, has_more=has_more),
        )

    # ── CSV Import ─────────────────────────────────────────────

    async def import_csv(
        self,
        tenant_id: uuid.UUID,
        file: UploadFile,
    ) -> CsvImportResponse:
        """Import customers from a CSV file.

        Columns: first_name, last_name, email, phone, address_line1,
        address_line2, city, county, postal_code, country
        """
        if not file.filename or not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV.",
            )

        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="CSV file must be under 10MB.",
            )

        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        if not reader.fieldnames or "first_name" not in reader.fieldnames or "last_name" not in reader.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must have at least 'first_name' and 'last_name' columns.",
            )

        total = 0
        created = 0
        skipped = 0
        errors: list[CsvImportError] = []
        batch: list[Customer] = []

        for row_num, row in enumerate(reader, start=2):  # 1-indexed, skip header
            total += 1

            first_name = (row.get("first_name") or "").strip()
            last_name = (row.get("last_name") or "").strip()

            if not first_name:
                errors.append(CsvImportError(row=row_num, field="first_name", message="Missing required field: first_name"))
                skipped += 1
                continue
            if not last_name:
                errors.append(CsvImportError(row=row_num, field="last_name", message="Missing required field: last_name"))
                skipped += 1
                continue

            email = (row.get("email") or "").strip() or None

            # Check duplicate email within batch + DB
            if email:
                existing_in_batch = any(c.email == email for c in batch)
                if existing_in_batch:
                    errors.append(CsvImportError(row=row_num, field="email", message="Duplicate email in CSV"))
                    skipped += 1
                    continue
                existing_in_db = await self.customer_repo.get_by_email(
                    self.session, email, [tenant_id],
                )
                if existing_in_db:
                    errors.append(CsvImportError(row=row_num, field="email", message="Email already exists in your company"))
                    skipped += 1
                    continue

            customer = Customer(
                tenant_id=tenant_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=(row.get("phone") or "").strip() or None,
                address_line1=(row.get("address_line1") or "").strip() or None,
                address_line2=(row.get("address_line2") or "").strip() or None,
                city=(row.get("city") or "").strip() or None,
                county=(row.get("county") or "").strip() or None,
                postal_code=(row.get("postal_code") or "").strip() or None,
                country=(row.get("country") or "RO").strip()[:2] or "RO",
            )
            batch.append(customer)
            created += 1

            # Flush batch every 100
            if len(batch) >= 100:
                await self.customer_repo.bulk_create(self.session, batch)
                batch = []

        # Flush remaining
        if batch:
            await self.customer_repo.bulk_create(self.session, batch)

        return CsvImportResponse(
            total=total,
            created=created,
            skipped=skipped,
            errors=errors,
        )

    # ── History ─────────────────────────────────────────────────

    async def get_history(
        self,
        tenant_ids: list[uuid.UUID],
        customer_id: uuid.UUID,
    ) -> CustomerHistorySummary:
        """Aggregated customer history across bounded contexts.

        Queries the appointments service directly via its repository
        (same database, avoiding HTTP overhead). Jobs/invoices/files
        are placeholders until those domains are built.
        """
        customer = await self.customer_repo.get_by_id(
            self.session, customer_id, tenant_ids,
        )
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found.",
            )

        notes_count = await self.note_repo.count_by_customer(
            self.session, customer_id, tenant_ids,
        )

        # ── Real appointment data ──────────────────────────
        from app.appointments.repository import AppointmentRepository

        appt_repo = AppointmentRepository()
        appt_total = await appt_repo.count_by_customer(self.session, customer_id, tenant_ids)
        appt_upcoming = await appt_repo.count_by_customer(
            self.session, customer_id, tenant_ids, upcoming_only=True,
        )
        appt_recent = await appt_repo.get_recent_by_customer(
            self.session, customer_id, tenant_ids, limit=5,
        )

        # ── Real job data ───────────────────────────────
        from app.jobs.repository import JobRepository

        job_repo = JobRepository()
        job_total = await job_repo.count_by_customer(self.session, customer_id, tenant_ids)
        job_active = await job_repo.count_by_customer(
            self.session, customer_id, tenant_ids, active_only=True,
        )
        job_recent = await job_repo.get_recent_by_customer(
            self.session, customer_id, tenant_ids, limit=5,
        )

        return CustomerHistorySummary(
            appointments={
                "total": appt_total,
                "upcoming": appt_upcoming,
                "recent": [
                    {
                        "id": str(a.id),
                        "title": a.title,
                        "scheduled_at": a.scheduled_at.isoformat(),
                        "status": a.status,
                    }
                    for a in appt_recent
                ],
            },
            jobs={
                "total": job_total,
                "active": job_active,
                "recent": [
                    {"id": str(j.id), "title": j.title, "status": j.status}
                    for j in job_recent
                ],
            },
            invoices={"total": 0, "paid": 0, "outstanding": 0, "last": None},
            files={"total": 0, "last_uploaded": None},
            notes_count=notes_count,
        )
