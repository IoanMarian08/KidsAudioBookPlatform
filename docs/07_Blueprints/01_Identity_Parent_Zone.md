# Blueprint 01 — Identity, Profiles and Protected Parent Zone

Version: 1.0  
Status: Implementation blueprint / unimplemented  
Owners: Identity + Family/Profiles, Mobile, QA

## 1. Outcome and scope

A parent can register, verify, sign in, recover, revoke sessions and manage child profiles. Children do **not** authenticate as independent adults. Entering Parent Zone triggers a protected, short-lived authorization step. The backend validates every privileged request irrespective of Flutter navigation.

**In scope:** account lifecycle, credentials/sessions, Parent Zone PIN/proof, child profile ownership, profile selection, parental preferences. Billing and playback enforcement belong to their separate modules.

**Normative sources:** [API Specification](../03_Architecture/API_Specification.md) §§14–23, [Security Architecture](../03_Architecture/Security_Architecture.md), [Database Design](../03_Architecture/Database_Design.md) §§7–8, [ADR-0005](../00_Project/ADR/ADR-0005-jwt-refresh-token-strategy.md), [ADR-0006](../00_Project/ADR/ADR-0006-parent-zone-security.md), [Product Bible](../00_Project/Product_Bible.md).

## 2. Public contracts to implement (existing paths)

| API path | Authorization/behavior |
|---|---|
| POST /auth/register and /auth/email-verification/confirm | Adult registration; single-use verification challenge |
| POST /auth/login, /auth/refresh, /auth/logout, /auth/logout-all | Revocable session + rotating refresh policy |
| POST /auth/password-reset/request and /confirm | Enumeration-resistant recovery |
| GET /sessions, DELETE /sessions/{sessionId} | Parent may revoke own sessions |
| GET /me, PATCH /me, POST /me/deletion-request | Account owner only, elevated for sensitive changes |
| POST /parent-zone/verify, PUT/DELETE /parent-zone/pin | PIN/challenge verification with rate limits; short-lived proof |
| GET/POST /child-profiles, GET/PATCH/DELETE /child-profiles/{profileId} | Parent-owned profile operations |
| POST /child-profiles/{profileId}/select | Changes active device session context |
| GET/PUT /child-profiles/{profileId}/preferences | Owner-checked settings |
| GET/PUT /child-profiles/{profileId}/parental-settings | **Requires Parent Zone proof** |

API error names/statuses are defined in [Error Catalog](../03_Architecture/Error_Catalog.md), not duplicated ad hoc here.

## 3. Suggested module package boundaries

~~~text
identity/
  api/                HTTP contracts, validation and filters
  application/        RegisterParent, VerifyContact, RotateSession, RevokeSession
  domain/             ParentAccount, AuthSession, SecurityChallenge policies
  infrastructure/     Repositories, hashers, clock, token and mail adapters

profiles/
  api/                Profile and preference controllers
  application/        CreateProfile, SelectProfile, UpdateParentalSettings
  domain/             ChildProfile, AgeBand, ProfileOwnership policy
  infrastructure/     JPA, event/outbox integration

parentzone/
  application/        VerifyChallenge, ElevateAccess, InvalidateProof
  domain/             ProofScope, AttemptLimiter, ChallengeState
  infrastructure/     Expiring proof adapter, key management
~~~

These are **responsibility sketches**, not required class names. No module may read another module's internal tables; share public application interfaces and immutable IDs.

## 4. Data ownership and invariants

Identity owns **identity.accounts, identity.authentication_methods, identity.sessions, identity.security_challenges**. Profiles owns **profiles.child_profiles, profile_preferences, parental_content_settings, parent_security_settings**. Do not store plain passwords or PINs.

Invariants:
- Every child profile belongs to exactly one authenticated adult account.
- Changing current profile does not grant authorization for an arbitrary profile ID.
- A revoked refresh token cannot be replayed to produce an active session.
- Parent Zone proof is bound to the correct account/session and expires; normal access token alone is insufficient for sensitive operations.
- Verify current password when removing a PIN as the API spec requires.
- Free/Premium profile-count quotas depend on approved commercial policy; **do not hard-code an invented limit**.
- Minimize child data; default to age band unless [DEC-008](../00_Project/DECISION_REGISTER.md) decides otherwise.

## 5. Critical runtime flows

~~~mermaid
sequenceDiagram
  actor Parent
  participant Flutter
  participant Identity
  participant Profiles
  Parent->>Flutter: Sign in
  Flutter->>Identity: POST /auth/login
  Identity-->>Flutter: Access + rotating refresh credentials
  Parent->>Flutter: Open Parent Zone
  Flutter->>Identity: POST /parent-zone/verify
  Identity-->>Flutter: Scoped, short-lived proof
  Parent->>Flutter: Update parental setting
  Flutter->>Profiles: PUT /child-profiles/{id}/parental-settings
  Profiles->>Identity: Validate owner + elevated scope
  Identity-->>Profiles: Authorization decision
  Profiles-->>Flutter: Updated settings or denial
~~~

Retries: registration/verification must not create duplicate accounts, proof replay must not bypass challenge limits, and profile updates require optimistic concurrency (see API If-Match guidance).

## 6. Failure and threat matrix

| Condition | Safe outcome | Test level |
|---|---|---|
| Unknown account at password reset | Identical public response/no enumeration | API/security |
| Expired email verification | Token rejected without account activation | Integration |
| Stolen/reused refresh token | Session family or reused credential revoked by policy | Integration/security |
| Child tries settings deep link | Challenge required, protected API denies | Mobile + API |
| Profile ID belongs to another parent | 403/404 per Error Catalog, no data leakage | API IDOR |
| Parent elevation expires mid-edit | Server rejects write, client can reauthenticate | E2E |
| Duplicate profile create request | Idempotent if key contracted, otherwise protected from accidental duplicate behavior | Integration |
| Redis cache unavailable | Authoritative user/session data consulted or fail closed for privilege | Resilience |

## 7. Test inventory

- Given two accounts, When account A requests B's profile ID, Then no data is returned.
- Given selected profile A, When switching to B, Then favorites, history, progress and cached screens do not retain A's private state.
- Given invalid PIN attempts, When threshold is reached, Then additional attempts are throttled/locked and audited.
- Given valid parent proof, When it expires, Then changing parental restrictions is rejected.
- Given access-token expiry, When rotating a valid refresh token, Then the old refresh credential is invalidated.
- Given unapproved profile quota, When implementing create-profile logic, Then it is backed by configurable entitlement policy, not guessed constants.

## 8. Done / outstanding decisions

Evidence: JUnit policy tests, Spring security integration tests, migrations/constraints, Flutter challenge/navigation tests, safe structured audit logs, explicit rate-limit metrics, OpenAPI compliance and session revocation demonstration.

Blocked until approved: parent consent text, age data/retention policy, free profile count, supported countries and credential policy details. Track [DEC-005, DEC-007, DEC-008](../00_Project/DECISION_REGISTER.md).
