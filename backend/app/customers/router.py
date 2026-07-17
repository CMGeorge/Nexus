"""Customers domain REST API router."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.deps import get_current_user, get_current_tenant_id, require_role
from app.core.tenant import get_accessible_tenant_ids
from app.customers.deps import get_customer_service
from app.customers.schemas import (
    CsvImportResponse,
    CustomerCreate,
    CustomerHistorySummary,
    CustomerListResponse,
    CustomerNoteCreate,
    CustomerNoteListResponse,
    CustomerNoteResponse,
    CustomerResponse,
    CustomerUpdate,
    MessageResponse,
)
from app.customers.service import CustomerService

router = APIRouter()


async def _resolve_tenant_ids(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_session),
) -> list[uuid.UUID]:
    """Resolve all accessible tenant IDs for hierarchical tenant support.

    Institution users see all branches; branch users see only their branch.
    """
    return await get_accessible_tenant_ids(tenant_id, session)


# ── Tenant-scoped dependency ──────────────────────────────────
TenantIdsDep = Depends(_resolve_tenant_ids)


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    data: CustomerCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    """Create a new customer for the current tenant.

    Requires: Employee, Manager, or Admin role.
    The customer's email must be unique within the tenant.
    """
    return await service.create(tenant_id, data)


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
    cursor: str | None = Query(None, description="Opaque cursor for the next page"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search across name, email, phone"),
    sort_by: str = Query("created_at", description="Sort field: first_name, last_name, email, created_at"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> CustomerListResponse:
    """List customers with cursor-based pagination.

    Supports full-text search across first_name, last_name, email, and phone.
    Institution-level users see customers from all branches.
    Requires: Employee, Manager, or Admin role.
    """
    return await service.list_customers(
        tenant_ids=tenant_ids,
        cursor=cursor,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        is_active=is_active,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    """Get a single customer by ID.

    Requires: Employee, Manager, or Admin role.
    Institution-level users can see branch-level customers.
    """
    return await service.get(tenant_ids, customer_id)


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: uuid.UUID,
    data: CustomerUpdate,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    """Partially update a customer (PATCH semantics).

    Requires: Employee, Manager, or Admin role.
    Only fields provided in the request body are updated.
    """
    return await service.update(tenant_ids, customer_id, data)


@router.delete("/{customer_id}", response_model=MessageResponse)
async def delete_customer(
    customer_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(require_role("Admin")),
    service: CustomerService = Depends(get_customer_service),
) -> MessageResponse:
    """Soft-delete a customer (sets is_active=False).

    Requires: Admin role only.
    The customer record is preserved for referential integrity.
    """
    return await service.deactivate(tenant_ids, customer_id)


@router.get("/{customer_id}/history", response_model=CustomerHistorySummary)
async def get_customer_history(
    customer_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerHistorySummary:
    """Get aggregated history for a customer across all domains.

    Requires: Employee, Manager, or Admin role.
    Returns placeholder data when downstream services are unavailable.
    """
    return await service.get_history(tenant_ids, customer_id)


@router.post("/{customer_id}/notes", response_model=CustomerNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_customer_note(
    customer_id: uuid.UUID,
    data: CustomerNoteCreate,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
) -> CustomerNoteResponse:
    """Add a note to a customer profile.

    Requires: Employee, Manager, or Admin role.
    """
    user_id = uuid.UUID(current_user["sub"])
    return await service.add_note(tenant_ids, customer_id, user_id, data)


@router.get("/{customer_id}/notes", response_model=CustomerNoteListResponse)
async def list_customer_notes(
    customer_id: uuid.UUID,
    tenant_ids: list[uuid.UUID] = TenantIdsDep,
    current_user: dict[str, Any] = Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
    cursor: str | None = Query(None, description="Opaque cursor for the next page"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> CustomerNoteListResponse:
    """List notes for a customer, newest first.

    Requires: Employee, Manager, or Admin role.
    """
    return await service.list_notes(tenant_ids, customer_id, cursor, limit)


@router.post("/import", response_model=CsvImportResponse)
async def import_customers_csv(
    file: UploadFile = File(...),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: dict[str, Any] = Depends(require_role("Admin", "Manager")),
    service: CustomerService = Depends(get_customer_service),
) -> CsvImportResponse:
    """Import customers from a CSV file.

    Requires: Manager or Admin role.
    CSV must have at least 'first_name' and 'last_name' columns.
    Max file size: 10MB.
    """
    return await service.import_csv(tenant_id, file)
