"""Auth domain Pydantic v2 schemas: requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

# ── Registration ───────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """Request body for user registration."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str | None = Field(None, max_length=100)
    last_name: str | None = Field(None, max_length=100)
    tenant_name: str = Field(min_length=1, max_length=200, description="Company name")

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        """Enforce password complexity: at least one digit, one uppercase, one lowercase."""
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v


class LoginRequest(BaseModel):
    """Request body for login.

    If the user has MFA enabled, a valid TOTP code must be provided.
    """

    email: EmailStr
    password: str
    totp_code: str | None = Field(
        None, min_length=6, max_length=6, pattern=r"^\d{6}$",
        description="Required if MFA is enabled for this account",
    )


class RefreshRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class MFASetupRequest(BaseModel):
    """Request body to initiate MFA setup."""

    pass  # No body needed; auth from bearer token


class MFAVerifyRequest(BaseModel):
    """Request body to verify MFA setup with a TOTP code."""

    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


# ── Responses ──────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Successful authentication response with JWT tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    """Public user profile."""

    id: uuid.UUID
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    is_verified: bool
    roles: list[str]
    mfa_enabled: bool
    tenant_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class MFASetupResponse(BaseModel):
    """Response after initiating MFA setup."""

    secret: str
    qr_code_uri: str
    backup_codes: list[str]


class MFAVerifyResponse(BaseModel):
    """Response after successfully verifying MFA setup."""

    message: str = "MFA has been enabled for your account"
    recovery_codes_remaining: int


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details response."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
