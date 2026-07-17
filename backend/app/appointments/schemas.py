"""Appointments domain Pydantic v2 schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AppointmentCreate(BaseModel):
    """Payload to create a new appointment."""

    customer_id: uuid.UUID = Field(description="Customer this appointment is for")
    assigned_to: uuid.UUID | None = Field(None, description="Employee assigned to this appointment")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None)
    scheduled_at: datetime = Field(description="ISO 8601 datetime of the appointment")
    duration_minutes: int = Field(60, ge=5, le=480, description="Duration in minutes")
    notes: str | None = Field(None)


class AppointmentUpdate(BaseModel):
    """Partial update — all fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None)
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(None, ge=5, le=480)
    assigned_to: uuid.UUID | None = Field(None)
    status: str | None = Field(None, pattern="^(confirmed|in_progress|completed|cancelled)$")
    notes: str | None = Field(None)


class AppointmentResponse(BaseModel):
    """Full appointment object."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_id: uuid.UUID
    assigned_to: uuid.UUID | None
    title: str
    description: str | None
    scheduled_at: datetime
    duration_minutes: int
    status: str
    notes: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AppointmentSummary(BaseModel):
    """Abbreviated appointment for list views."""

    id: uuid.UUID
    customer_id: uuid.UUID
    assigned_to: uuid.UUID | None
    title: str
    scheduled_at: datetime
    duration_minutes: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CursorMeta(BaseModel):
    """Cursor pagination metadata."""

    next: str | None = None
    has_more: bool = False


class AppointmentListResponse(BaseModel):
    """Cursor-paginated list."""

    data: list[AppointmentSummary]
    cursor: CursorMeta


class MessageResponse(BaseModel):
    """Generic message."""

    message: str