"""Customers domain Pydantic v2 schemas: requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Request Schemas ────────────────────────────────────────────


class CustomerCreate(BaseModel):
    """Payload to create a new customer."""

    first_name: str = Field(
        ..., min_length=1, max_length=100,
        description="Customer's given name",
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100,
        description="Customer's family name",
    )
    email: str | None = Field(
        None, max_length=255,
        description="Email address. Must be unique within the tenant.",
    )
    phone: str | None = Field(
        None, max_length=30,
        description="Phone number in E.164 format preferred",
    )
    address_line1: str | None = Field(None, max_length=255, description="Primary street address")
    address_line2: str | None = Field(None, max_length=255, description="Secondary street address")
    city: str | None = Field(None, max_length=100, description="City name")
    county: str | None = Field(None, max_length=100, description="County / județ (Romania)")
    postal_code: str | None = Field(None, max_length=20, description="Postal / ZIP code")
    country: str | None = Field(
        None, min_length=2, max_length=2,
        description="ISO 3166-1 alpha-2 country code, defaults to 'RO'",
    )


class CustomerUpdate(BaseModel):
    """Payload to partially update a customer. All fields optional."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=30)
    address_line1: str | None = Field(None, max_length=255)
    address_line2: str | None = Field(None, max_length=255)
    city: str | None = Field(None, max_length=100)
    county: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, min_length=2, max_length=2)


class CustomerNoteCreate(BaseModel):
    """Payload to add a note to a customer profile."""

    content: str = Field(..., min_length=1, description="Free-text note content")


# ── Response Schemas ───────────────────────────────────────────


class CustomerResponse(BaseModel):
    """Full customer object returned for detail views."""

    id: uuid.UUID = Field(description="Public customer identifier (UUID)")
    tenant_id: uuid.UUID = Field(description="Owning tenant ID")
    first_name: str = Field(description="Customer's given name")
    last_name: str = Field(description="Customer's family name")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address_line1: str | None = Field(None, description="Primary street address")
    address_line2: str | None = Field(None, description="Secondary street address")
    city: str | None = Field(None, description="City name")
    county: str | None = Field(None, description="County / județ")
    postal_code: str | None = Field(None, description="Postal / ZIP code")
    country: str | None = Field(None, description="ISO 3166-1 alpha-2 country code")
    is_active: bool = Field(description="Whether the customer is active")
    created_at: datetime = Field(description="ISO 8601 UTC timestamp of creation")
    updated_at: datetime = Field(description="ISO 8601 UTC timestamp of last update")

    model_config = {"from_attributes": True}


class CustomerSummary(BaseModel):
    """Abbreviated customer object for list views (no full address)."""

    id: uuid.UUID = Field(description="Public customer identifier (UUID)")
    first_name: str = Field(description="Customer's given name")
    last_name: str = Field(description="Customer's family name")
    email: str | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    city: str | None = Field(None, description="City name")
    is_active: bool = Field(description="Whether the customer is active")
    created_at: datetime = Field(description="ISO 8601 UTC timestamp of creation")
    updated_at: datetime = Field(description="ISO 8601 UTC timestamp of last update")

    model_config = {"from_attributes": True}


class CursorMeta(BaseModel):
    """Cursor pagination metadata."""

    next: str | None = Field(
        None, description="Opaque cursor for the next page. Null if no more results.",
    )
    has_more: bool = Field(description="True if there are more results beyond this page")


class CustomerListResponse(BaseModel):
    """Cursor-paginated list of customers."""

    data: list[CustomerSummary] = Field(description="List of customer summaries")
    cursor: CursorMeta = Field(description="Pagination cursor metadata")


class CustomerNoteAuthor(BaseModel):
    """Brief author info embedded in note responses."""

    id: uuid.UUID = Field(description="User ID of the note author")
    first_name: str | None = Field(None, description="Author's given name")
    last_name: str | None = Field(None, description="Author's family name")


class CustomerNoteResponse(BaseModel):
    """Single note with author information."""

    id: uuid.UUID = Field(description="Note identifier (UUID)")
    customer_id: uuid.UUID = Field(description="Customer this note belongs to")
    content: str = Field(description="Note content")
    created_by: CustomerNoteAuthor = Field(description="Platform user who wrote the note")
    created_at: datetime = Field(description="ISO 8601 UTC timestamp of creation")
    updated_at: datetime = Field(description="ISO 8601 UTC timestamp of last update")

    model_config = {"from_attributes": True}


class CustomerNoteListResponse(BaseModel):
    """Cursor-paginated list of customer notes."""

    data: list[CustomerNoteResponse] = Field(description="List of notes")
    cursor: CursorMeta = Field(description="Pagination cursor metadata")


class CsvImportError(BaseModel):
    """A single error encountered during CSV import."""

    row: int = Field(description="Row number in the CSV (1-indexed, header row skipped)")
    field: str | None = Field(None, description="Field name that caused the error")
    message: str = Field(description="Human-readable error message")


class CsvImportResponse(BaseModel):
    """Summary of a CSV import operation."""

    total: int = Field(description="Total rows in the CSV (excluding header)")
    created: int = Field(description="Number of customers successfully created")
    skipped: int = Field(description="Number of rows skipped due to validation errors")
    errors: list[CsvImportError] = Field(
        default_factory=list, description="Detailed errors for skipped rows",
    )


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str = Field(description="Human-readable status message")


class CustomerHistorySummary(BaseModel):
    """Aggregated history for a customer across all bounded contexts."""

    appointments: dict = Field(
        default_factory=lambda: {"total": 0, "upcoming": 0, "last": None},
        description="Appointment summary (from appointments context)",
    )
    jobs: dict = Field(
        default_factory=lambda: {"total": 0, "active": 0, "last": None},
        description="Job/work-order summary (from jobs context)",
    )
    invoices: dict = Field(
        default_factory=lambda: {"total": 0, "paid": 0, "outstanding": 0, "last": None},
        description="Invoice summary (from invoices context)",
    )
    files: dict = Field(
        default_factory=lambda: {"total": 0, "last_uploaded": None},
        description="File summary (from files context)",
    )
    notes_count: int = Field(0, description="Number of notes attached to this customer")
