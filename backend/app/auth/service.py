"""Auth domain service: registration, login, token management, MFA."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from redis.asyncio import Redis

import json
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.repository import RefreshTokenRepository, UserRepository
from app.auth.schemas import (
    MessageResponse,
    MFASetupResponse,
    MFAVerifyResponse,
    TokenResponse,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_backup_codes,
    generate_totp_secret,
    get_totp_uri,
    hash_password,
    verify_password,
    verify_totp,
)
from app.core.tenant import Tenant


class AuthService:
    """Authentication and authorization business logic."""

    def __init__(
        self,
        session: AsyncSession,
        redis: "Redis[Any] | None" = None,
    ):
        self.user_repo = UserRepository(session)
        self.token_repo = RefreshTokenRepository(session)
        self.session = session
        self.redis = redis

    # ── Registration ───────────────────────────────────────────

    async def register(
        self,
        email: str,
        password: str,
        first_name: str | None,
        last_name: str | None,
        tenant_name: str,
    ) -> TokenResponse:
        """Register a new user and their tenant (company).

        Creates both a tenant record and a user record in one transaction.
        Returns JWT tokens for immediate login.
        """
        # Check for duplicate email
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        # Create tenant (company)
        tenant_id = uuid.uuid4()
        tenant = Tenant(
            id=tenant_id,
            name=tenant_name,
            subdomain=None,  # Set later when tenant configures their domain
            is_active=True,
        )
        self.session.add(tenant)

        # Create user

        # Create user
        user = User(
            email=email,
            hashed_password=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            tenant_id=tenant_id,
            roles="Admin",  # First user is always admin
        )
        await self.user_repo.create(user)

        # Generate tokens
        return await self._issue_tokens(user)

    # ── Login ──────────────────────────────────────────────────

    async def login(self, email: str, password: str, totp_code: str | None = None) -> TokenResponse:
        """Authenticate user with email and password.

        If MFA is enabled, a valid TOTP code must be provided.
        """
        user = await self.user_repo.get_by_email(email)

        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        # MFA enforcement
        if user.mfa_enabled:
            if totp_code is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA is enabled for this account. Provide a valid TOTP code.",
                )
            if user.mfa_secret is None or not verify_totp(user.mfa_secret, totp_code):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )

        return await self._issue_tokens(user)

    # ── Token refresh ──────────────────────────────────────────

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token.

        Rotates the refresh token: old one is revoked, new one issued.
        """
        payload = decode_refresh_token(refresh_token_str)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        jti = payload.get("jti")
        if jti is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        # Verify token exists in DB and is not revoked
        stored_token = await self.token_repo.find_valid(jti)
        if stored_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked or expired",
            )

        # Revoke old token (rotation)
        await self.token_repo.revoke(jti)

        # Fetch user
        user = await self.user_repo.get_by_id(uuid.UUID(payload["sub"]))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated",
            )

        return await self._issue_tokens(user)

    # ── Logout ─────────────────────────────────────────────────

    async def logout(self, refresh_token_str: str) -> MessageResponse:
        """Invalidate a refresh token so it can no longer be used."""
        payload = decode_refresh_token(refresh_token_str)
        if payload is not None:
            jti = payload.get("jti")
            if jti is not None:
                await self.token_repo.revoke(jti)

                # Also blacklist in Redis for faster checks
                if self.redis is not None:
                    ttl = settings.refresh_token_expire_days * 86400
                    await self.redis.setex(f"blacklist:refresh:{jti}", ttl, "1")

        return MessageResponse(message="Successfully logged out")

    # ── MFA Setup ──────────────────────────────────────────────

    async def mfa_setup(self, user_id: uuid.UUID) -> MFASetupResponse:
        """Generate a TOTP secret and backup codes for MFA setup."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA is already enabled for this account",
            )

        secret = generate_totp_secret()
        backup_codes = generate_backup_codes()
        qr_code_uri = get_totp_uri(secret, user.email)

        # Store secret and backup codes (MFA not yet enabled until verified)
        await self.user_repo.update_mfa_secret(user.id, secret, backup_codes)

        return MFASetupResponse(
            secret=secret,
            qr_code_uri=qr_code_uri,
            backup_codes=backup_codes,
        )

    # ── MFA Verify ─────────────────────────────────────────────

    async def mfa_verify(self, user_id: uuid.UUID, code: str) -> MFAVerifyResponse:
        """Verify a TOTP code and enable MFA for the user."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA is already enabled",
            )

        if user.mfa_secret is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA setup has not been initiated. Call /mfa/setup first.",
            )

        if not verify_totp(user.mfa_secret, code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        await self.user_repo.enable_mfa(user.id)

        backup_codes: list[str] = json.loads(user.mfa_backup_codes or "[]")
        return MFAVerifyResponse(
            message="MFA has been enabled for your account",
            recovery_codes_remaining=len(backup_codes),
        )

    # ── Helpers ────────────────────────────────────────────────

    async def _issue_tokens(self, user: User) -> TokenResponse:
        """Create and store JWT token pair for a user."""
        user_id_str = str(user.id)
        tenant_id_str = str(user.tenant_id)
        roles = [r.strip() for r in user.roles.split(",") if r.strip()]

        access_token = create_access_token(user_id_str, tenant_id_str, roles)
        refresh_token = create_refresh_token(user_id_str, tenant_id_str)

        # Decode to get JTI and expiration for storage
        payload = decode_refresh_token(refresh_token)
        if payload is not None:
            await self.token_repo.create(
                jti=payload["jti"],
                user_id=user.id,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
            )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )
