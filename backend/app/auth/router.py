"""Auth domain REST API router."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.deps import get_auth_service
from app.auth.schemas import (
    LoginRequest,
    MessageResponse,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.core.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Register a new user and their company (tenant).

    Creates both the tenant and the user, returning JWT tokens for immediate login.
    The first user of a tenant is always assigned the 'Admin' role.
    """
    return await auth_service.register(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        tenant_name=data.tenant_name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate with email and password.

    Returns access token (15 min) and refresh token (7 days).
    """
    return await auth_service.login(
        email=data.email,
        password=data.password,
        totp_code=data.totp_code,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Refresh an access token using a valid refresh token.

    The old refresh token is revoked and a new one issued (rotation).
    """
    return await auth_service.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    data: RefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Logout by revoking the refresh token.

    The access token remains valid until it expires (15 min).
    """
    return await auth_service.logout(data.refresh_token)


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFASetupResponse:
    """Initiate MFA setup for the current user.

    Returns a TOTP secret and QR code URI. MFA is not active until /mfa/verify is called.
    """
    user_id = UUID(current_user["sub"])
    return await auth_service.mfa_setup(user_id)


@router.post("/mfa/verify", response_model=MFAVerifyResponse)
async def mfa_verify(
    data: MFAVerifyRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MFAVerifyResponse:
    """Verify TOTP code and enable MFA for the current user.

    Requires a prior call to /mfa/setup.
    """
    user_id = UUID(current_user["sub"])
    return await auth_service.mfa_verify(user_id, data.code)
