# ADR-0005: JWT and Refresh Token Strategy

- **Status:** Accepted
- **Date:** 2026-07-14
- **Decision owners:** Architecture, Backend, Security
- **Review cadence:** At least annually and after any authentication incident

## Context

The mobile application and admin dashboard require stateless API authentication, secure session renewal, device-level revocation, and support for horizontal scaling. Access tokens must remain short-lived, while users should not be forced to authenticate repeatedly during normal use.

The platform is used on shared family devices and includes child profiles, premium subscriptions, parent-only operations, account recovery, offline playback, and administrative access. Authentication therefore needs to distinguish between account identity, device sessions, child-profile context, and short-lived parent elevation.

The design must minimize the impact of stolen credentials, support explicit logout and remote session revocation, avoid storing reusable secrets in plaintext, and remain operable during key rotation and partial dependency outages.

## Decision

Use signed JWT access tokens and opaque rotating refresh tokens.

- Access tokens expire after 10 minutes.
- Refresh tokens expire after 30 days for normal sessions and 7 days for elevated-risk sessions.
- Refresh tokens are random, high-entropy opaque values.
- Only a SHA-256 hash of each refresh token is persisted.
- Refresh tokens are rotated on every successful refresh.
- Reuse of an already-rotated token revokes the entire token family.
- Each refresh token is bound to one device session.
- Mobile credentials are stored only in platform secure storage.
- Admin sessions use secure, HttpOnly, SameSite cookies through a backend-for-frontend or protected admin API.
- Security-sensitive operations may require recent authentication or a separate parent-elevation credential.

## Authentication Model

The authentication model separates four concerns:

1. **Account identity** — the authenticated parent or guardian account.
2. **Device session** — one installation or browser session associated with the account.
3. **Profile context** — the active child profile selected within the authenticated account.
4. **Elevation context** — short-lived proof that a parent-only verification step succeeded.

An access token proves account authentication and session identity. It does not independently prove that a child-profile identifier supplied by the client is valid or owned by the account. Profile context is validated by the backend for every profile-scoped request.

## Access Token Contract

Access tokens are JWTs signed using an asymmetric algorithm approved by the security baseline. They are never encrypted unless a future threat model explicitly requires token confidentiality in addition to integrity.

Required claims:

```json
{
  "sub": "account-uuid",
  "sid": "session-uuid",
  "roles": ["PARENT"],
  "scope": ["catalog:read", "profile:write"],
  "iat": 1784040000,
  "nbf": 1784040000,
  "exp": 1784040600,
  "iss": "kids-audio-book-platform",
  "aud": "mobile-api",
  "jti": "token-uuid"
}
```

Rules:

- `sub` identifies the account, not a child profile.
- `sid` identifies the current device session.
- `roles` and `scope` are authorization hints and must still be checked against server-side policy where required.
- `jti` enables incident analysis and emergency deny-listing for exceptional cases.
- Tokens must not contain passwords, PINs, refresh tokens, payment details, subscription receipts, personal child data, or secrets.
- Clock-skew tolerance must be small and explicitly configured.
- Clients must not parse token claims to make security-sensitive entitlement decisions.

## Refresh Token Record

The persisted refresh-session record contains:

- refresh-token hash;
- token-family ID;
- session ID;
- account ID;
- device ID or installation identifier;
- issued timestamp;
- expiry timestamp;
- last-used timestamp;
- rotation timestamp;
- previous-token reference where operationally useful;
- revocation timestamp and reason;
- authentication assurance level;
- IP and device risk metadata;
- user-agent or application version metadata where appropriate;
- created and updated audit fields.

Plaintext refresh tokens are returned only once to the client and are never persisted, logged, traced, or included in analytics.

## Refresh Flow

1. The client submits the current refresh token over TLS.
2. The backend hashes the token and loads the matching active session record.
3. The backend verifies expiry, revocation state, account state, device binding, and risk policy.
4. The current token is marked consumed.
5. A new refresh token is generated and stored as a hash in the same token family.
6. A new short-lived access token is issued.
7. The response returns the new access token and new plaintext refresh token.
8. The rotation is committed atomically.

The old refresh token becomes invalid immediately after a successful rotation.

## Reuse Detection

If a consumed or replaced refresh token is presented again:

1. mark the token family as compromised;
2. revoke every active token in that family;
3. invalidate the associated session;
4. emit a security event;
5. require the user to authenticate again;
6. optionally notify the account owner based on risk policy.

Reuse detection must distinguish between benign concurrent retries and likely theft. The refresh endpoint therefore supports idempotent handling for the same successful exchange within a very short server-controlled window, without allowing multiple independent descendant tokens.

## Session Lifecycle

A session can be:

- `ACTIVE`;
- `ROTATING` during an atomic refresh operation;
- `REVOKED`;
- `EXPIRED`;
- `COMPROMISED`;
- `LOCKED` pending risk review.

Revocation reasons include:

- explicit logout;
- logout from all devices;
- password change;
- account disablement or deletion;
- refresh-token reuse;
- administrator action;
- security incident;
- excessive risk score;
- inactivity or expiry.

Expired and revoked session records are retained only for the period required for security investigation, abuse prevention, and legal obligations, then removed or anonymized.

## Logout Semantics

### Logout Current Device

Revoke the current refresh-token family and clear client credentials.

### Logout All Devices

Revoke every active session for the account. Existing access tokens may remain technically valid until their short expiry, unless emergency deny-listing is activated.

### Password Change or Recovery

By default, revoke all existing refresh-token families unless product and security explicitly approve preserving trusted sessions.

## Key Management

- Use asymmetric signing keys.
- Publish public verification keys through a JWKS endpoint.
- Every JWT includes a `kid` header.
- Signing keys are stored in a managed secret or key-management system.
- Private keys never appear in source control, logs, build output, or application configuration committed to the repository.
- Rotate keys on a defined schedule and immediately after suspected exposure.
- Keep previous public keys available until all tokens signed with them have expired.
- Validate that key rotation works in staging before production activation.
- Unknown `kid` values fail closed and generate operational metrics.

## Admin Session Rules

Admin access has a higher risk profile than the consumer mobile application.

- Prefer secure, HttpOnly cookies rather than browser-accessible bearer tokens.
- Use `Secure` and an appropriate `SameSite` policy.
- Protect state-changing operations against CSRF.
- Require stronger authentication and shorter session lifetime for privileged roles.
- Require recent re-authentication for role changes, account suspension, refunds, data exports, and security configuration.
- Admin sessions must support immediate revocation.
- Session fixation must be prevented by rotating the session identifier after authentication and privilege elevation.

## Mobile Storage Rules

- Store access and refresh credentials only in Keychain, Android Keystore-backed storage, or equivalent secure storage.
- Never store tokens in shared preferences, plain SQLite tables, logs, crash reports, screenshots, clipboard, or analytics payloads.
- Clear credentials on logout, account deletion, invalid refresh, or secure-storage corruption.
- Device backup and restore behavior must be tested so credentials are not unintentionally cloned to another device.
- Rooted or compromised device signals may reduce refresh lifetime or require re-authentication but must not be treated as perfectly reliable.

## Authorization Rules

- Authentication and authorization are separate concerns.
- Backend policy remains authoritative for roles, scopes, profile ownership, subscription state, and parent-zone requirements.
- Child-profile selection is represented by server-validated context.
- A token issued before a critical role or account-state change may be rejected through session-state checks for sensitive endpoints.
- Service-to-service authentication must use separate credentials and audiences, not consumer access tokens.

## Failure Behavior

### Access Token Expired

Return a stable authentication error. The client may perform one refresh attempt, then retry the original request once.

### Refresh Token Expired or Revoked

Return a stable session-expired error and require login.

### Token Signature or Claim Invalid

Reject without attempting refresh when the token is structurally invalid, has the wrong issuer or audience, or uses an unsupported signing algorithm.

### Session Store Unavailable

- Existing access-token validation may continue for low-risk reads if policy allows.
- Refresh, logout, revocation, and sensitive operations fail closed.
- The failure must be observable and alertable.

### Clock Drift

Use a small configured tolerance and monitor repeated clock-related validation failures.

## Rate Limiting and Abuse Prevention

Apply independent limits for:

- login attempts by account, IP, and device;
- refresh attempts by session and IP;
- password recovery;
- verification-code submission;
- parent PIN verification;
- token-family reuse events.

Rate limits must not expose whether an account exists. Progressive delay, cooldown, CAPTCHA or additional verification may be introduced based on risk.

## Audit and Security Events

Record structured events for:

- login success and failure;
- refresh success and failure;
- token rotation;
- token reuse detection;
- current-device logout;
- logout-all-devices;
- forced revocation;
- password change and recovery;
- signing-key rotation;
- invalid issuer, audience, algorithm, or key identifier;
- administrator session elevation.

Events contain correlation ID, session ID, account ID where lawful, device metadata, outcome, reason code, and risk indicators. Raw credentials and sensitive payloads are never recorded.

## Observability

Track at minimum:

- login success and failure rate;
- refresh success, failure, and latency;
- active session count;
- refresh-token reuse detections;
- forced revocations;
- invalid JWT reason distribution;
- unknown `kid` occurrences;
- session-store availability;
- rate-limit activations;
- authentication-related support incidents.

Alerts should focus on sustained failure spikes, unusual reuse patterns, key-discovery failures, and widespread refresh errors.

## Testing Requirements

Automated tests must cover:

- valid token issuance and validation;
- issuer, audience, expiry, not-before, signature, and algorithm rejection;
- refresh rotation;
- concurrent refresh requests;
- token-family reuse detection;
- logout current device and all devices;
- account disablement and deletion;
- password-change revocation;
- key rotation and overlapping JWKS keys;
- secure cookie behavior for admin sessions;
- rate limiting;
- dependency failure and fail-closed behavior;
- log redaction and absence of plaintext credentials.

Contract tests verify stable error codes for mobile and admin clients.

## Operational Runbook Expectations

The authentication runbook must document:

- emergency signing-key rotation;
- revoking all sessions for one account;
- revoking all platform sessions in a severe incident;
- identifying token-family reuse;
- handling unknown-key failures;
- session-store recovery;
- disabling refresh temporarily while preserving safe access where possible;
- validating that secrets are absent from logs and traces.

## Consequences

### Positive

- Stateless access-token validation supports horizontal scaling.
- Short access-token lifetime limits compromise duration.
- Refresh-token rotation reduces the value of stolen long-lived credentials.
- Device-level and account-level revocation remain possible.
- Asymmetric signing supports distributed verification and controlled key rotation.

### Negative

- Access tokens can remain valid until expiry unless an emergency deny list or session check is used.
- Token-family tracking adds persistence, cleanup, and concurrency complexity.
- Secure mobile storage and browser-cookie behavior require platform-specific testing.
- Key rotation and incident response require disciplined operations.

## Rejected Alternatives

- **Long-lived JWTs without refresh tokens:** excessive compromise window and weak revocation.
- **Persisted server sessions for every API request:** unnecessary lookup cost for normal stateless validation.
- **Persisted plaintext refresh tokens:** unacceptable credential exposure risk.
- **Reusable non-rotating refresh tokens:** weaker theft detection and containment.
- **Client-only authorization decisions:** incompatible with server-authoritative security and entitlements.
- **Shared signing secret across all components:** increases blast radius and complicates controlled verification.

## Follow-up Actions

- Define the authentication error codes in `Error_Catalog.md`.
- Document Parent Zone elevation separately in ADR-0006.
- Add session tables and indexes to `Database_Design.md`.
- Add authentication metrics and alerts to `Logging_Monitoring.md`.
- Add key-rotation and session-revocation procedures to the operations handbook.
- Validate mobile secure-storage behavior on iOS and Android.

## Decision Compliance

A change is compliant with this ADR only when it preserves short-lived access tokens, opaque rotating refresh tokens, hashed persistence, token-family reuse detection, device-level revocation, asymmetric signing, secure client storage, and server-authoritative authorization.