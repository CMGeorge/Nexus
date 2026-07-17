"""Unit tests for AuthService business logic."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from tests.auth.conftest import TEST_EMAIL, TEST_PASSWORD, TEST_TENANT_NAME


class TestAuthServiceRegister:
    """Tests for AuthService.register()."""

    @pytest.mark.asyncio
    async def test_register_creates_user_and_tenant(self, test_session: AsyncSession):
        """Registration creates both a User and a Tenant row."""
        service = AuthService(session=test_session)

        result = await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )

        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"

        # Verify user was created
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        assert user is not None
        assert user.email == TEST_EMAIL
        assert user.roles == "Admin"
        assert user.tenant_id is not None

        # Verify tenant was created
        from sqlalchemy import select
        from app.core.tenant import Tenant

        tenant = (await test_session.execute(
            select(Tenant).where(Tenant.id == user.tenant_id)
        )).scalar_one_or_none()
        assert tenant is not None
        assert tenant.name == TEST_TENANT_NAME
        assert tenant.is_active is True

    @pytest.mark.asyncio
    async def test_register_duplicate_email_rejected(self, test_session: AsyncSession):
        """Registering with an existing email returns 409."""
        service = AuthService(session=test_session)

        # First registration
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="First",
            last_name="User",
            tenant_name="First Company",
        )

        # Second registration with same email
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.register(
                email=TEST_EMAIL,
                password=TEST_PASSWORD,
                first_name="Second",
                last_name="User",
                tenant_name="Second Company",
            )
        assert exc.value.status_code == 409
        assert "already exists" in exc.value.detail

    @pytest.mark.asyncio
    async def test_register_first_user_is_admin(self, test_session: AsyncSession):
        """First registered user gets Admin role."""
        service = AuthService(session=test_session)
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Admin",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        assert user.roles == "Admin"


class TestAuthServiceLogin:
    """Tests for AuthService.login()."""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, test_session: AsyncSession):
        """Login with correct email/password returns tokens."""
        service = AuthService(session=test_session)
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )

        result = await service.login(email=TEST_EMAIL, password=TEST_PASSWORD)
        assert result.access_token is not None
        assert result.refresh_token is not None

    @pytest.mark.asyncio
    async def test_login_wrong_password_returns_401(self, test_session: AsyncSession):
        """Login with wrong password returns 401."""
        service = AuthService(session=test_session)
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.login(email=TEST_EMAIL, password="WrongPass1")
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_mfa_enabled_requires_code(self, test_session: AsyncSession):
        """Login with MFA enabled but no code returns 401 with MFA message."""
        service = AuthService(session=test_session)
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )
        # Manually enable MFA on the user
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        user.mfa_enabled = True
        user.mfa_secret = "JBSWY3DPEHPK3PXP"  # Known test secret
        await test_session.commit()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.login(email=TEST_EMAIL, password=TEST_PASSWORD)
        assert exc.value.status_code == 401
        assert "MFA is enabled" in exc.value.detail

    @pytest.mark.asyncio
    async def test_login_mfa_invalid_code_returns_401(self, test_session: AsyncSession):
        """Login with MFA enabled and wrong code returns 401."""
        service = AuthService(session=test_session)
        await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        user.mfa_enabled = True
        user.mfa_secret = "JBSWY3DPEHPK3PXP"
        await test_session.commit()

        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.login(email=TEST_EMAIL, password=TEST_PASSWORD, totp_code="000000")
        assert exc.value.status_code == 401
        assert "Invalid MFA code" in exc.value.detail


class TestAuthServiceLogout:
    """Tests for AuthService.logout()."""

    @pytest.mark.asyncio
    async def test_logout_revokes_token(self, test_session: AsyncSession):
        """Logout with valid refresh token revokes it."""
        service = AuthService(session=test_session)
        result = await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )

        logout_result = await service.logout(result.refresh_token)
        assert "Successfully logged out" in logout_result.message

        # Token should now be revoked
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            await service.refresh(result.refresh_token)
        assert exc.value.status_code == 401


class TestAuthServiceMFA:
    """Tests for MFA setup and verification."""

    @pytest.mark.asyncio
    async def test_mfa_setup_generates_secret_and_codes(self, test_session: AsyncSession):
        """MFA setup returns a secret, QR URI, and backup codes."""
        service = AuthService(session=test_session)
        result = await service.register(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            first_name="Test",
            last_name="User",
            tenant_name=TEST_TENANT_NAME,
        )

        # Get user ID from token (simplified: fetch user directly)
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        mfa_result = await service.mfa_setup(user.id)

        assert len(mfa_result.secret) > 0
        assert mfa_result.qr_code_uri.startswith("otpauth://")
        assert len(mfa_result.backup_codes) > 0
        # User should have stored secret but MFA not yet enabled
        user = await service.user_repo.get_by_email(TEST_EMAIL)
        assert user.mfa_secret is not None
        assert user.mfa_enabled is False