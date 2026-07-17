"""Jobs domain Pydantic v2 schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Payload to create a new job."""

    customer_id: uuid.UUID = Field(description="Customer this job is for")
    appointment_id: uuid.UUID | None = Field(None, description="Optional source appointment")
    assigned_to: uuid.UUID | None = Field(None, description="Assigned employee")
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None)
    estimated_hours: float | None = Field(None, ge=0)
    notes: str | None = Field(None)


class JobUpdate(BaseModel):
    """Partial update — all fields optional."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None)
    assigned_to: uuid.UUID | None = Field(None)
    status: str | None = Field(None, pattern="^(pending|in_progress|completed|invoiced|cancelled)$")
    estimated_hours: float | None = Field(None, ge=0)
    actual_hours: float | None = Field(None, ge=0)
    parts_cost: float | None = Field(None, ge=0)
    labor_cost: float | None = Field(None, ge=0)
    notes: str | None = Field(None)


class JobResponse(BaseModel):
    """Full job object."""

    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_id: uuid.UUID
    appointment_id: uuid.UUID | None
    assigned_to: uuid.UUID | None
    title: str
    description: str | None
    status: str
    estimated_hours: float | None
    actual_hours: float | None
    parts_cost: float | None
    labor_cost: float | None
    notes: str | None
    is_active: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobSummary(BaseModel):
    """Abbreviated job for list views."""

    id: uuid.UUID
    customer_id: uuid.UUID
    assigned_to: uuid.UUID | None
    title: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CursorMeta(BaseModel):
    next: str | None = None
    has_more: bool = False


class JobListResponse(BaseModel):
    data: list[JobSummary]
    cursor: CursorMeta


class MessageResponse(BaseModel):
    message: str