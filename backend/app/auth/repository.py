"""Auth domain repository: data access for User and RefreshToken."""

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User


class UserRepository:
    """Data access for the users table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email (unique across all tenants)."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Find a user by primary key."""
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Insert a new user."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_mfa_secret(
        self, user_id: uuid.UUID, secret: str, backup_codes: list[str]
    ) -> None:
        """Store the TOTP secret and backup codes for a user."""
        import json

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                mfa_secret=secret,
                mfa_backup_codes=json.dumps(backup_codes),
            )
        )
        await self.session.flush()

    async def enable_mfa(self, user_id: uuid.UUID) -> None:
        """Mark MFA as enabled for a user."""
        await self.session.execute(
            update(User).where(User.id == user_id).values(mfa_enabled=True)
        )
        await self.session.flush()


class RefreshTokenRepository:
    """Data access for refresh_tokens table."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, jti: str, user_id: uuid.UUID, expires_at: datetime
    ) -> RefreshToken:
        """Store a new refresh token."""
        token = RefreshToken(token_jti=jti, user_id=user_id, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        return token

    async def find_valid(self, jti: str) -> RefreshToken | None:
        """Find a refresh token by JTI that is not revoked and not expired."""
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.token_jti == jti,
                RefreshToken.is_revoked == False,  # noqa: E712
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, jti: str) -> None:
        """Revoke a refresh token by JTI."""
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_jti == jti)
            .values(is_revoked=True)
        )
        await self.session.flush()
