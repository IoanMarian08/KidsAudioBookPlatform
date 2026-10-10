# 14 — Functional State Matrices, Cross-Cutting Transitions and Edge Cases

**Purpose:** A testable source of state invariants used by Flutter, staff UI and independently deployed microservices.
**Authority:** [API Spec](../../03_Architecture/API_Specification.md), [Error Catalog](../../03_Architecture/Error_Catalog.md), [Product Bible](../../00_Project/Product_Bible.md). This chapter does not redefine enum names or invent new HTTP endpoints.

## 1. Adult session and Parent Zone verification

| Current condition | Trigger | Effective result | Guard |
|---|---|---|---|
| Signed out | Sign in succeeds | Adult session active | Credentials valid |
| Pending verification | Correct single-use code | Verified status | Unexpired challenge |
| Session active | Parent Zone entry | Challenge required or valid scoped proof | Recent parent verification |
| Proof active | Expiry/logout/profile ownership mismatch | Protected write denied | Service validates scope/expiry |
| Session active | Logout all | Sessions revoked | Server authority and client cleanup |
| Session active | Password reset | Active credentials follow revocation policy | Approved auth controls |
| Suspended account | Request any protected resource | Deny | No stale client bypass |

## 2. Child profile and content eligibility

| State/change | Required effect | Forbidden behavior |
|---|---|---|
| Profile selected | Scope home/favorites/history/progress to owned profile | Read sibling cache |
| Profile changed | Clear old context, reauthorize audio | Continue foreign listening session |
| Age band reduced | Filter catalog/playback | Show higher age story from stale link |
| Blocked category added | Hide/deny disallowed stories | Ignore restriction in offline grant |
| Profile archived | Deny new context and resources | Restore via old local ID |
| Story Draft/In review | Staff-only visibility | Appear in child search |
| Story Published | Eligible only if age/locale/entitlement allow | Treat published as universal permit |
| Story Suspended | Deny new playback/media grants | Continue signing new URL from cache |
| Media scan fails | Keep private/quarantined | Mark published-ready |

## 3. Listening session and progress

| Input | Domain result | Security note |
|---|---|---|
| Eligible Play | Authorized new/reused session | Verify selected profile and story authority |
| Same Play retried | Dedup per session/idempotency contract | Avoid duplicate records |
| Pause | Save/freeze current time | Not a completed story |
| Seek | Clamp and re-sync text/illustration | Seek to end not automatic completion |
| Explicit completion | One qualified completed state | Duplicate cannot affect counters twice |
| Stale offline update after completion | Preserve completion | Server wins over stale partial |
| Another profile tries session ID | Deny | No cross-profile playback metadata |
| Expired signed URL | Obtain new authorized grant or show safe error | Never assume forever valid |
| Content taken down | Deny new session/grant | Cached catalog data insufficient |

## 4. Downloads and offline

| State | User action | Result | Integrity |
|---|---|---|---|
| No download | Request with valid rights | Grant created | Owner/profile/device bound |
| Queued | Start | Downloading | Partial bytes not Ready |
| Downloading | Cancel/connection loss | Canceled or paused/retryable | No unsafe play |
| Downloading | Transfer completes | Verifying | Required checksum |
| Verifying | Checksum matches | Ready, confirmed | License/grant valid |
| Verifying | Mismatch | Failed/quarantined | Corrupt bytes not played |
| Ready | Device offline | Play if rights policy permits | Local license unexpired |
| Ready | Entitlement revoked | Follow approved local revocation TTL | No new online grant |
| Ready | Remove | Deleted | Account/profile-scoped |
| Local progress queued | Reconnect | Per-change sync result | Replay dedup; preserve completed |

## 5. Subscription and account plan states

| Provider-confirmed condition | Capability effect | Visible parent explanation |
|---|---|---|
| Free | Only Free-eligible content/features | Current plan clearly shown |
| Eligible Trial | Approved temporary Premium features | Terms and expiry accurately shown |
| Active paid | Premium until provider period end | Renewal/cancellation details |
| Canceled auto-renew | Keep active rights through valid paid period | Not falsely Expired |
| Billing grace | Approved provider policy | Payment problem without child alarm |
| Payment pending | No unverified Premium grant | Verification in progress |
| Expired | Deny new Premium grants | Parent manage/renew path |
| Refunded/revoked | Remove new paid rights | Parent explanation; offline policy |
| Unknown provider state | Reconcile; safe authorization | Never fake success |

## 6. Notifications, support and deletion

- Notification unread -> read -> dismissed; repeated read/dismiss is idempotent and account-scoped.
- Marketing consent enabled -> withdrawn: future optional sends stop; required safety/account notices follow policy.
- Device registered -> token replaced -> signed out/deleted: former device must not receive previous household messages.
- Support form draft -> submitted/pending -> confirmed or failure; retry must not create uncontrolled duplicate requests.
- Account Active -> Deletion Requested -> Processing -> Completed only after all owning services confirm; policy may allow Cancellation before irreversible work; Failed/Retry pending is not Completed.
- An account deletion after a store purchase does not by itself prove Apple/Google subscription cancellation.

## 7. Remote service and network failure behavior

| Dependency failure | Child-facing handling | Authority handling |
|---|---|---|
| identity-service unavailable | Safe authenticated-state failure | No privileged write without proof |
| profiles-service unavailable | Avoid showing foreign profile | No unauthorized stream grant |
| catalog-service unavailable | Retry or approved local list | No new unverified publication access |
| billing-service unavailable | Parent sees verification pending | No unverified new Premium |
| media-service/CDN unavailable | Buffering/retry, preserves position | No private object key leak |
| playback-service unavailable | Player recovery/offline if licensed | No invented progress success |
| notifications-service unavailable | Inbox or push unavailable | Does not block approved audio |
| RabbitMQ delayed | Pending background work | Outbox retained, idempotent replay |
| One service database down | Scope incident to owning service | No foreign database fallback |

## 8. Feature flags and invalid assumptions

Gated advertising must remain off without approval. Trial offers must be configured by market and provider; account profile limits are not invented. Parent consent, age data format, deletion grace, locale set, offline license window and deployment provider are all decisions recorded in Decision Register. Configuration errors should fail to the most conservative allowed state without sacrificing basic approved Free stories.

## 9. QA state transition checklist

For each state transition test:
1. allowed actor and invalid actor;
2. current profile versus foreign profile;
3. initial, repeated, delayed and reordered event;
4. online, offline and mid-request network loss;
5. entitlement activated/revoked during operation;
6. content approved/suspended during operation;
7. UI cancellation and safe repeat;
8. localization, screen reader, reduced motion;
9. server persistence and audit evidence;
10. independent service timeout, recovery and event replay.

Each requirement above maps to detailed acceptance scenarios in chapters 01–12; reference those IDs when writing tests. No new state transition should be merged solely because a UI happy path works.
