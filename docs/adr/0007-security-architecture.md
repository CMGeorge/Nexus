# ADR-0007: Security Architecture — API Gateway, JWT, Rate Limiting, and MFA

## Status
Accepted

## Date
2026-07-15

## Context
Nexus is a multi-tenant SaaS platform handling sensitive business data (customer PII, invoices, appointment records) across multiple small-business tenants. The platform must defend against OWASP Top-10 API threats while maintaining clear separation between frontend, API, and backend layers. Without a formal security architecture, the platform risks cross-tenant data leakage, token theft, credential brute-force, and denial-of-service via unauthenticated endpoints.

### Requirements
1. **Frontend/API/Backend separation** — The React/Vue frontend must never connect directly to PostgreSQL or Redis. The FastAPI REST layer is the single entry point for all data access.
2. **JWT authentication** — Short-lived access tokens (15 minutes) + longer-lived refresh tokens (7 days) with rotation and blacklisting. Role-based claims (Admin, Manager, Employee, Customer) embedded in the token payload.
3. **Rate limiting** — Redis-based sliding window, scoped per-tenant AND per-endpoint, with tiered limits configurable by subscription tier.
4. **MFA** — TOTP (Time-based One-Time Password) as primary second factor, with email OTP as fallback.

## Decision

### 1. API Gateway Pattern — Traefik as Single Entry Point

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌────────────┐
│ Frontend │────▶│   Traefik    │────▶│  FastAPI      │────▶│ PostgreSQL │
│ (React)  │     │  (Reverse    │     │  (REST API)   │     │ + Redis    │
│          │     │   Proxy)     │     │               │     │            │
│ Mobile   │────▶│              │     │               │     │            │
│ (Swift)  │     │              │     │               │     │            │
└──────────┘     └──────────────┘     └──────────────┘     └────────────┘
```

- **Traefik** is the sole ingress point for all HTTP traffic
- All `/api/*` routes are forwarded to the FastAPI backend
- Frontend static assets are served by Traefik directly (or CDN in production)
- The database and Redis are on an internal Docker network — **no external exposure**
- Frontend never possesses database credentials; all data access is via REST API with JWTs

### 2. JWT Token Architecture

#### Token Lifecycle
| Token Type | Lifetime | Storage | Rotation |
|---|---|---|---|
| Access Token | 15 minutes | Memory only (frontend), never localStorage | Not rotated (short-lived) |
| Refresh Token | 7 days | HttpOnly, Secure, SameSite=Strict cookie | Rotated on each use (old token invalidated) |

#### Token Payload Structure
```json
{
  "sub": "user-uuid-here",
  "tenant_id": "company-uuid-here",
  "roles": ["admin"],
  "iat": 1689000000,
  "exp": 1689000900,
  "jti": "unique-token-id",
  "type": "access"
}
```

#### Refresh Token Rotation
- Each refresh request invalidates the previous refresh token (stored in Redis blacklist with TTL matching original expiry)
- New access + refresh token pair issued
- If a revoked refresh token is reused → all user tokens are revoked (token reuse detection)

#### Token Blacklisting
- Blacklist stored in Redis with key `blacklist:{jti}` and TTL matching token expiry
- Access token validation checks blacklist on every request
- Logout endpoint adds current access token + refresh token to blacklist

### 3. Rate Limiting Architecture

#### Sliding Window Algorithm (Redis)
```
Key: ratelimit:{tenant_id}:{endpoint_group}:{window_timestamp}
Value: request count
TTL: window_size * 2
```

#### Tiered Limits
| Tier | Auth Endpoints | CRUD Endpoints | File Uploads | Tenant Configurable |
|---|---|---|---|---|
| Free | 30 req/min | 200 req/min | 10 req/min | No |
| Pro | 100 req/min | 1000 req/min | 50 req/min | Yes |
| Enterprise | 300 req/min | 5000 req/min | 200 req/min | Yes |

#### Enforcement Points
- **Traefik level**: Global rate limiting (all IPs, all endpoints) — coarse-grained, first line of defense
- **FastAPI middleware**: Per-tenant, per-endpoint-group — fine-grained, subscription-aware
- **Response headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`

#### Rate Limit Response (RFC 6585)
```json
{
  "type": "https://api.nexus.app/errors/rate-limited",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Retry after 30 seconds.",
  "instance": "/api/v1/customers"
}
```

### 4. MFA Integration Points
- TOTP enrollment: `POST /api/v1/auth/mfa/enroll` → returns QR code URI + backup codes
- TOTP verification: `POST /api/v1/auth/mfa/verify` → returns JWT with `mfa_verified` claim
- Email OTP fallback: `POST /api/v1/auth/mfa/email-otp` → sends 6-digit code via email
- Remember-device: hashed device fingerprint stored, MFA skipped for 30 days on trusted device
- See ADR-0008 for full MFA design

### 5. Additional Security Hardening

| Control | Implementation |
|---|---|
| **CORS** | Traefik middleware: allow only known frontend origins |
| **Security Headers** | Traefik: HSTS, X-Content-Type-Options, X-Frame-Options, CSP |
| **HTTPS** | Traefik TLS termination with Let's Encrypt auto-renewal |
| **SQL Injection** | SQLAlchemy 2.0 ORM exclusively — no raw SQL, no `text()` without bind parameters |
| **Input Validation** | Pydantic v2 strict mode on all request schemas |
| **Audit Logging** | Every mutation writes to `audit_logs` table: who, what, when, old/new values |
| **Secrets Management** | Environment variables via Docker secrets, never in code or config files |
| **Dependency Scanning** | GitHub Dependabot + `uv lock --check` in CI |

## Rationale

### Why Traefik over Nginx/Caddy?
- Native Docker/Consul service discovery — automatic route configuration when containers start
- Middleware plugin architecture for rate limiting, auth, headers
- Let's Encrypt integration built-in
- Already selected in the Nexus stack (consistent with existing architecture)

### Why 15-minute Access Tokens?
- OWASP recommends short-lived access tokens for API security
- 15 minutes balances security (stolen token window is small) with usability (not refreshing constantly)
- Refresh token rotation mitigates long-lived token theft

### Why Redis Sliding Window over Token Bucket?
- Sliding window provides smoother rate limiting (no burst at window boundary)
- Native Redis sorted-set implementation is O(log N) per request
- Per-tenant keys enable subscription-tier-aware limiting

### Why TOTP over WebAuthn/Passkeys?
- TOTP has near-universal device support (Google Authenticator, Authy, 1Password, etc.)
- No hardware token requirement — lower barrier to adoption for small business users
- WebAuthn can be added later as a premium option (see Alternatives)

## Consequences

### Positive
- **Zero-trust architecture**: Frontend has no database access, all operations gated through auth'd API
- **Token reuse detection**: Automated revocation on suspected theft
- **Graceful degradation**: Rate limiting prevents one noisy tenant from impacting others
- **Auditability**: Every data mutation logged with tenant + user context
- **Defense in depth**: Rate limiting at both Traefik (coarse) and FastAPI (fine-grained) layers

### Negative
- **Redis dependency for token validation**: Every API request checks Redis blacklist — Redis becomes critical path
- **Token rotation complexity**: Refresh token rotation requires careful client-side handling to avoid race conditions
- **Rate limit Redis load**: Sliding window with sorted sets generates more Redis operations than token bucket
- **MFA UX friction**: TOTP enrollment adds onboarding steps for every user

### Mitigations
- Redis Sentinel/Cluster for HA (patroni-managed already)
- Client SDKs handle token refresh with mutex to prevent race conditions
- Rate limit counters batched in Redis pipeline
- MFA enrollment is one-time; remember-device reduces daily friction

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Nginx as reverse proxy | Traefik already selected; switching adds migration cost without clear benefit |
| 5-minute access tokens | Too frequent refresh requests; increased Redis load; poor UX on mobile |
| Token bucket rate limiting | Burst at window boundary allows short spikes that can overwhelm services |
| WebAuthn/Passkeys only | Lower device support among target SMB users; many still use devices without biometric/passkey support |
| JWT-only (no refresh tokens) | Long-lived access tokens are a security risk; no way to revoke without blacklist check on every request |
| OAuth2/OIDC with external IdP | Adds external dependency; Nexus targets self-contained deployment for SMBs; can be added later as SSO option |

## References
- Redmine epic: #504 — Security Architecture Hardening
- Redmine task-packet: #505 — [Design] Infrastructure
- Redmine task-packet: #506 — [Design] Backend API
- Related ADR: ADR-0008 — Multi-Factor Authentication
- OWASP API Security Top-10: https://owasp.org/API-Security/
- RFC 7807 (Problem Details): https://datatracker.ietf.org/doc/html/rfc7807
- RFC 6585 (429 Too Many Requests): https://datatracker.ietf.org/doc/html/rfc6585
- RFC 6238 (TOTP): https://datatracker.ietf.org/doc/html/rfc6238
