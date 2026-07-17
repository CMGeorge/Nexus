"""JWT token creation/verification, bcrypt password hashing, and MFA helpers."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import bcrypt
import pyotp
from jose import JWTError, jwt

from app.core.config import settings

# ── Password hashing ──────────────────────────────────────────


def hash_password(password: str) -> str:
    """Return bcrypt hash of the plain-text password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plain-text password against its bcrypt hash."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


# ── JWT ───────────────────────────────────────────────────────


def _create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    """Create a signed JWT with expiration."""
    to_encode = data.copy()
    now = datetime.now(UTC)
    to_encode.update(
        {
            "exp": now + expires_delta,
            "iat": now,
            "jti": str(uuid4()),
        }
    )
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str, tenant_id: str, roles: list[str]) -> str:
    """Create an access token (short-lived, 15 min default)."""
    return _create_token(
        data={"sub": user_id, "tenant_id": tenant_id, "roles": roles, "type": "access"},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: str, tenant_id: str) -> str:
    """Create a refresh token (long-lived, 7 days default)."""
    return _create_token(
        data={"sub": user_id, "tenant_id": tenant_id, "type": "refresh"},
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate any JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and validate an access token."""
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    return payload


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a refresh token."""
    payload = decode_token(token)
    if payload is None or payload.get("type") != "refresh":
        return None
    return payload


# ── MFA (TOTP) ────────────────────────────────────────────────


def generate_totp_secret() -> str:
    """Generate a new random TOTP secret."""
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str) -> str:
    """Return the otpauth:// URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.mfa_issuer)


def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code against the stored secret."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code)


def generate_backup_codes(count: int = 8) -> list[str]:
    """Generate a list of one-time backup codes."""
    import secrets

    return [secrets.token_hex(4) for _ in range(count)]
