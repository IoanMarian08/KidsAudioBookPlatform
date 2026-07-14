# ADR-0005: JWT and Refresh Token Strategy

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture and Backend

## Context

The mobile application and admin dashboard require stateless API authentication, secure session renewal, device-level revocation, and support for future horizontal scaling. Access tokens must remain short-lived, while users should not be forced to log in repeatedly.

## Decision

Use signed JWT access tokens and opaque refresh tokens.

- Access tokens expire after 10 minutes.
- Refresh tokens expire after 30 days for normal sessions and 7 days for elevated-risk sessions.
- Refresh tokens are random opaque values; only a SHA-256 hash is persisted.
- Refresh tokens are rotated on every successful refresh.
- Reuse of an already-rotated token revokes the complete token family.
- Each refresh token is bound to a device session and stores account ID, device ID, token family ID, issued time, expiry, last use, IP risk metadata, and revocation reason.
- Mobile access tokens are stored only in platform-secure storage.
- Admin sessions use secure, HttpOnly, SameSite cookies through a backend-for-frontend or protected admin API.

## Token Claims

Required access-token claims:

```json
{
  "sub": "account-uuid",
  "sid": "session-uuid",
  "roles": ["PARENT"],
  "scope": ["catalog:read", "profile:write"],
  "iat": 1784040000,
  "exp": 1784040600,
  "iss": "kids-audio-book-platform",
  "aud": "mobile-api"
}
```

Child-profile selection is represented by a server-validated profile context, not by trusting a freely supplied profile ID from the client.

## Security Rules

- Use asymmetric signing keys and publish a JWKS endpoint.
- Rotate signing keys without invalidating all active sessions.
- Never store passwords, PINs, subscription details, or child-sensitive data in tokens.
- Validate issuer, audience, signature, expiry, not-before, and session status.
- Reject tokens associated with disabled or deleted accounts.
- Rate-limit login and refresh endpoints.
- Record security events for login success, login failure, refresh reuse, logout, and forced revocation.

## Consequences

### Positive

- Stateless access-token validation supports horizontal scaling.
- Session revocation remains possible through refresh-session state.
- Rotation reduces the impact of stolen refresh tokens.

### Negative

- Access tokens remain valid until expiry unless an emergency deny list is used.
- Token-family tracking adds persistence and cleanup logic.

## Rejected Alternatives

- Long-lived JWTs without refresh tokens: excessive compromise window.
- Persisted server sessions for every API call: unnecessary coupling and lookup cost.
- Persisted plaintext refresh tokens: unacceptable credential exposure risk.
