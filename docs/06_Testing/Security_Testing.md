# Security and Child-Safety Testing

Version: 2.0.0  
Status: Mandatory security verification standard  
Owner: Security / Backend / QA

## 1. Threat-driven scope

Test authentication, authorization, protected Parent Zone, privacy of child profiles, verified billing, signed media URLs, editorial upload/publishing, messaging and infrastructure boundaries. Use OWASP ASVS and Mobile Application Security testing concepts appropriate to risk.

Testing must not use actual children's personal data, real billing credentials, or external systems without authorization.

## 2. Core test matrix

| ID | Attack scenario | Required assertion |
|---|---|---|
| SEC-001 | Cross-account child ID substitution (IDOR) | Denied regardless of guessing or UUID knowledge |
| SEC-002 | Child route/deep link to Parent Zone mutation | Server requires valid elevated adult scope |
| SEC-003 | Expired/replayed refresh token | Rotation invalidates previous credential |
| SEC-004 | Brute force PIN/password | Rate limits/lockout and safe logging |
| SEC-005 | Forged premium receipt/provider callback | No entitlement without valid provider verification |
| SEC-006 | Signed audio URL expired/tampered | Denied by storage/CDN policy |
| SEC-007 | Draft/suspended story forced authorization | Cannot issue valid new playback grants |
| SEC-008 | Uploaded file MIME/polyglot/malware | Rejected/quarantined pending scan |
| SEC-009 | SQL injection/search injection | Input rejected or safely parameterized |
| SEC-010 | XSS/CSRF/session abuse in Admin | Sanitized content and suitable auth/CSRF defenses |
| SEC-011 | Queue duplicate/replay poison event | Idempotent effect, bounded DLQ handling |
| SEC-012 | Logging access tokens/child PII | Sanitization prevents leak |
| SEC-013 | Deleted/archived profile direct access | Not found/forbidden, no data disclosure |
| SEC-014 | Rate limit denial of service | Safe throttling without starving critical operations |

## 3. Security testing layers

**Static:** SAST, dependency scanning/SCA, secret scanning, infrastructure policy and SBOM scanning in CI.  
**Dynamic:** DAST against staging, authenticated/unauthenticated API security tests, media authorization and upload adversarial fixtures.  
**Manual:** threat modeling at feature design and penetration review before major releases.  
**Mobile:** local data encryption at rest, secure key storage, device credential/session handling, deep-link boundary, logs/clipboard/backups.  
**Operational:** secret rotation drill, incident notification, recovery and log-access audit.

## 4. Parent Zone and child-specific abuse cases

- A child must not reach purchase, account deletion, downloads/privacy controls or parental restrictions by switching tabs, restoring state, push link or direct API call.
- Biometric success locally is not itself authorization to change server records; test server elevation expiry.
- No behavioral ad targeting of children; any approved ad flow must pass age-suitability/privacy and app-store policy review.
- Recommenders must never surface unreviewed content.
- Profile switching must clear private UI/cache material from the previous profile.

## 5. Secure test operations

Only approved staging/sandbox targets; no destructive fuzzing on production. Redact evidence and store it with restricted access. A security finding includes reproduction steps, impact, affected identities/scopes, severity, owner, remediation and regression test.

## 6. Vulnerability gates

Critical exploitable findings, authorization bypass, child data exposure, forged premium grants, malware publication or unapproved sensitive-data sharing block release. Medium/low exceptions require a documented owner, compensating control and expiry date; they do not quietly disappear from dashboards.

## 7. Security sign-off checklist

[ ] Access matrix covered with positive and negative tests  
[ ] Parent Zone elevation verified server-side  
[ ] Payment callback authenticity and refund revocation validated  
[ ] Private media URLs and upload scanning tested  
[ ] Mobile deep link/offline-storage review complete  
[ ] CI SAST/SCA/secret scanning pass  
[ ] Logging/telemetry data minimization verified  
[ ] Incident and responsible disclosure procedures ready

Related: [Security Architecture](../03_Architecture/Security_Architecture.md), [Testing Strategy](Testing_Strategy.md), [Infrastructure](../05_DevOps/Infrastructure.md).
