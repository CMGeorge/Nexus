# ADR-0008: Multi-Factor Authentication — TOTP, Enrollment, Backup Codes, Remember-Device

## Status
Accepted

## Date
2026-07-15

## Context
Nexus handles sensitive small-business data including customer PII, appointment schedules, invoices with payment information, and employee records. A compromised password alone should not grant access. Multi-factor authentication (MFA) is required to meet industry-standard security practices and protect against credential stuffing, phishing, and password reuse attacks.

### Requirements
1. **TOTP as primary MFA method** — Time-based One-Time Password (RFC 6238) compatible with Google Authenticator, Authy, 1Password, and other standard TOTP apps.
2. **Email OTP as fallback** — For users who cannot or will not use a TOTP app, a 6-digit code sent via email.
3. **Enrollment flow** — Guided setup with QR code display, verification step, and backup code generation.
4. **Backup codes** — One-time-use recovery codes for when the TOTP device is lost.
5. **Remember-device** — Option to skip MFA on trusted devices for 30 days.

## Decision

### 1. MFA Enrollment Flow

```
User → "Enable MFA" → Server generates TOTP secret
     → Displays QR code (otpauth:// URI)
     → User scans with authenticator app
     → User enters TOTP code for verification
     → Server verifies, marks MFA as enrolled
     → Server generates 10 backup codes (displayed once)
     → User confirms backup codes saved
```

#### API Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/mfa/enroll` | Initiate enrollment, return `otpauth://` URI + QR code |
| `POST` | `/api/v1/auth/mfa/verify` | Verify TOTP code to complete enrollment or authenticate |
| `POST` | `/api/v1/auth/mfa/email-otp` | Request/send email OTP code |
| `POST` | `/api/v1/auth/mfa/email-otp/verify` | Verify email OTP code |
| `GET`  | `/api/v1/auth/mfa/backup-codes` | Generate new backup codes (requires current TOTP) |
| `POST` | `/api/v1/auth/mfa/recover` | Authenticate using a backup code |
| `DELETE`| `/api/v1/auth/mfa/remember-device` | Revoke all remembered devices |
| `DELETE`| `/api/v1/auth/mfa` | Disable MFA (requires current TOTP or backup code) |

### 2. TOTP Implementation

#### Secret Generation
- Per-user 160-bit secret, generated with `secrets.token_bytes(20)`
- Encoded as Base32 for TOTP app compatibility
- Stored encrypted at rest using AES-256-GCM with a key derived from the tenant-specific KEK (Key Encryption Key)
- The plaintext secret is never logged or returned after enrollment

#### QR Code
- Format: `otpauth://totp/Nexus:{email}?secret={base32_secret}&issuer=Nexus&algorithm=SHA1&digits=6&period=30`
- QR code rendered server-side and returned as inline SVG or PNG data URI (not a separate request)
- Displayed only during enrollment, never stored

#### Verification
- RFC 6238 standard: `TOTP = HMAC-SHA1(secret, counter)`, where counter = floor(unix_time / 30)
- Accept current and adjacent intervals (±1 step, 90-second window) to account for clock skew
- Rate limited: 5 failed attempts per 15 minutes per user
- On successful verification, the user's `mfa_enrolled` flag is set and `mfa_verified_at` timestamp updated

#### Token Claims After MFA
```json
{
  "sub": "user-uuid",
  "tenant_id": "company-uuid",
  "roles": ["admin"],
  "mfa_verified": true,
  "mfa_method": "totp",
  "iat": 1689000000,
  "exp": 1689000900,
  "jti": "unique-token-id"
}
```

### 3. Email OTP Fallback

#### Flow
1. User selects "Send email code" on MFA challenge screen
2. `POST /api/v1/auth/mfa/email-otp` → sends 6-digit code to user's verified email
3. Code is numeric, 6 digits, valid for 10 minutes
4. User enters code → `POST /api/v1/auth/mfa/email-otp/verify`
5. Valid code grants `mfa_verified` claim in JWT

#### Security Controls
- Rate limited: 1 email OTP per 60 seconds per user
- Maximum 3 email OTP requests per 15 minutes
- Code is stored in Redis with key `mfa:email_otp:{user_id}` and TTL 600 seconds
- Code is hashed (SHA-256) before Redis storage; comparison is hash-to-hash
- Failed verification attempts: 5 max per code before code is invalidated

### 4. Backup Codes

#### Generation
- 10 codes per set, each 8 characters (alphanumeric, uppercase for readability)
- Format: `XXXX-XXXX`
- Stored as SHA-256 hashes in `user_backup_codes` table
- Only the hashes are persisted; plaintext codes shown once during generation
- User can regenerate (invalidates all previous codes)

#### Verification
- User enters backup code on MFA challenge screen
- Server hashes the input and checks against stored hashes
- Match → code is deleted (one-time use) → JWT with `mfa_verified` claim issued
- Used backup code count displayed to user after login
- When ≤ 3 codes remain → warning displayed post-login

#### Database Schema
```sql
CREATE TABLE user_backup_codes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES companies(id),
    code_hash VARCHAR(64) NOT NULL,  -- SHA-256 hex digest
    used_at TIMESTAMPTZ,              -- NULL = unused
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(user_id, code_hash)
);
CREATE INDEX idx_backup_codes_user ON user_backup_codes(user_id, tenant_id) WHERE used_at IS NULL;
```

### 5. Remember-Device

#### Mechanism
- On successful MFA verification, user can check "Remember this device for 30 days"
- Server generates a device token: random 256-bit value, stored in `remembered_devices` table
- Device token set as HttpOnly, Secure, SameSite=Strict cookie: `nexus_device_token`
- On subsequent logins, if `nexus_device_token` cookie is present and matches a valid record → MFA step is skipped
- Device fingerprint stored alongside token: `user_agent` hash + `ip_prefix` (/24) for binding

#### Security Controls
- Device token is single-use: validated, then rotated on each successful login
- Bound to user agent family + IP prefix — major change invalidates the token
- Max 5 remembered devices per user; oldest is evicted
- Revoke all remembered devices via `DELETE /api/v1/auth/mfa/remember-device`
- All remembered devices revoked on password change

#### Database Schema
```sql
CREATE TABLE remembered_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES companies(id),
    device_token_hash VARCHAR(64) NOT NULL,
    device_name VARCHAR(255),          -- User-friendly label
    user_agent_hash VARCHAR(64),       -- SHA-256 of browser UA
    ip_prefix INET,                    -- /24 prefix of last IP
    last_used_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,   -- now() + 30 days
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_remembered_devices_user ON remembered_devices(user_id, tenant_id);
```

### 6. MFA Enforcement Policy

| User Action | MFA Required? |
|---|---|
| Login (password auth) | Yes, if enrolled |
| Token refresh | No (refresh token already proves prior auth) |
| Password change | Yes (re-verify MFA) |
| MFA enrollment | Yes (verify TOTP code) |
| MFA disable | Yes (TOTP or backup code) |
| Remembered device login | No (within 30 days, same device) |
| API key / service account | No (machine-to-machine auth, separate mechanism) |

## Rationale

### Why TOTP as Primary?
- Universal app support across iOS and Android (Google Authenticator, Authy, Microsoft Authenticator, 1Password, Bitwarden)
- No SMS dependency (SMS is vulnerable to SIM swap and incurs per-message costs)
- Offline-capable: TOTP codes work without internet connectivity on the user's device
- Industry standard (RFC 6238), well-understood security properties

### Why Email OTP as Fallback (not SMS)?
- Email is already verified for account operations (password reset, notifications)
- No per-message cost like SMS
- Users in Nexus target market (small businesses) always have email access
- SMS is vulnerable to SIM-swap attacks; email accounts typically have stronger protections (and can themselves have MFA)

### Why Backup Codes (not Recovery Email)?
- Recovery email introduces a circular dependency: losing access to TOTP device likely also means losing access to email (same phone)
- Backup codes are offline-recoverable: printed or saved, no second factor needed
- One-time-use property limits exposure if codes are discovered

### Why Remember-Device with 30-Day Expiry?
- 30 days balances UX convenience with security — frequent enough to re-verify possession
- Device binding (UA + IP prefix) prevents token theft from being trivially reusable on a different device
- Rotation on each use prevents replay attacks

## Consequences

### Positive
- **Phishing resistance**: Stolen password alone cannot authenticate
- **Offline recovery**: Backup codes provide account recovery without support intervention
- **Reduced support load**: Self-service MFA enrollment and recovery
- **Audit trail**: All MFA events logged (enrollment, verification, backup code use, device changes)

### Negative
- **Onboarding friction**: Every user must enroll in MFA (mitigated by remember-device)
- **Support for lost devices**: Users who lose both TOTP device AND backup codes require admin reset
- **Redis dependency**: Email OTP codes and rate limit counters stored in Redis
- **Backup code secure storage burden**: Users must safely store 10 codes (education needed)

### Mitigations
- Admin-initiated MFA reset flow for locked-out users (with identity verification)
- Redis HA via Patroni-managed Sentinel (already in architecture)
- In-app backup code re-download prompt at login if count ≤ 3
- Clear UX guidance during enrollment: "Save these codes somewhere safe, like a password manager"

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| SMS OTP as primary | SIM-swap vulnerability, per-message cost, deliverability issues in target SMB markets |
| WebAuthn/FIDO2 only | Lower adoption among non-technical SMB users; many lack hardware tokens or biometric-equipped devices |
| No MFA (password only) | Unacceptable for platform handling PII and financial data (invoices) |
| Third-party MFA provider (Auth0, Okta) | Adds external dependency and per-user cost; Nexus targets self-contained deployment |
| Push notification MFA | Requires companion mobile app for push delivery; Nexus mobile app is not GA yet |
| Email as primary MFA | Email accounts can be compromised; TOTP provides stronger second-factor isolation |
| No backup codes (admin reset only) | Creates support bottleneck; self-service recovery scales better for multi-tenant SaaS |

## References
- Redmine epic: #504 — Security Architecture Hardening
- Redmine task-packet: #506 — [Design] Backend API
- Related ADR: ADR-0007 — Security Architecture
- RFC 6238 (TOTP): https://datatracker.ietf.org/doc/html/rfc6238
- RFC 4226 (HOTP): https://datatracker.ietf.org/doc/html/rfc4226
- OWASP Multi-Factor Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html
