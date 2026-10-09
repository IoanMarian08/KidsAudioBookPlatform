# Data Ownership Matrix

Version: 1.0.0  
Status: Active Draft  
Owner: Project Architecture  
Last updated: 2026-07-15

## 1. Purpose

This document defines authoritative data ownership across KidsAudioBookPlatform. It complements the C4 views by making ownership, read access, write access, retention, and extraction boundaries explicit.

The matrix applies whether capabilities run inside the initial modular monolith or as independently deployed services later.

A shared database does not imply shared ownership.

## 2. Core Rules

1. Every business record has exactly one owning bounded context.
2. Only the owning context may create, update, or delete authoritative records.
3. Other contexts use public application contracts, APIs, events, projections, or controlled exports.
4. Direct cross-context repository access is prohibited.
5. Direct cross-context table writes are prohibited.
6. Cached or projected data is never authoritative unless explicitly stated.
7. Ownership changes require an ADR and a migration plan.
8. Sensitive child and parent data must be minimized outside the owning context.
9. Historical and audit records follow explicit retention and immutability rules.
10. Extraction into a service must preserve the ownership defined here.

## 3. Ownership Matrix

| Bounded context | Authoritative data | Allowed consumers | Preferred access | Notes |
|---|---|---|---|---|
| Identity and Access | Parent accounts, credentials, account status, sessions, refresh-token families, devices, roles | Profiles, Subscriptions, Administration, Audit | Application interface, API, security events | Credentials and token material never leave the context |
| Family and Profiles | Child profiles, age bands, avatars, language, accessibility preferences, parental settings | Catalog, Listening, Notifications, Recommendations, Administration | Application interface, profile events, read models | Child profile is not an authentication principal |
| Catalog and Editorial | Stories, series, episodes, categories, collections, publication state, localized metadata | Listening, Media, Recommendations, Search, Notifications, Administration | Catalog API, publication events, projections | Publication state is authoritative only here |
| Media | Asset metadata, uploads, checksums, processing status, renditions, manifests | Catalog, Listening, Downloads, Administration | Media API, asset events, signed access | Binary objects live in object storage; metadata lives in PostgreSQL |
| Listening and Progress | Playback sessions, resume positions, completion, history, favorites | Recommendations, Analytics, Child Experience, Administration support views | Listening API, playback events, projections | Progress reconciliation follows offline-sync rules |
| Subscriptions and Billing | Purchases, provider transactions, plan lifecycle, renewals, refunds, store callbacks | Entitlements, Notifications, Administration, Audit | Billing API, subscription events | Provider state is normalized but raw evidence is retained safely |
| Entitlements | Effective free, trial, premium, grace, and feature eligibility | Listening, Downloads, Catalog, Advertising, Mobile API | Entitlement decision API, entitlement events, short-lived cache | No client may authoritatively compute entitlement |
| Advertising Policy | Eligibility, session counters, suppression rules, ad-decision history | Mobile API, Analytics, Administration | Decision API, policy events | No advertising inside story playback |
| Downloads and Offline | Device download authorization, manifests, offline expiry, reconciliation state | Mobile application, Entitlements, Listening, Security Monitoring | Download API, revocation events | Local device copies are not authoritative business state |
| Ambient Audio | Soundscape metadata, availability, mixing defaults | Mobile application, Catalog, Administration | API and catalog projection | User-local mix state may remain device-owned |
| Notifications | Notification records, preferences, templates, device registrations, delivery attempts | Mobile API, Admin support, Analytics | Notification API, delivery events | Business services never call providers directly |
| Administration | Admin workflow state, support cases, moderation notes, dashboard projections | Authorized administrators, Audit | Admin API and dedicated projections | Administration does not take ownership of domain records it manages |
| Audit and Compliance | Immutable security and administrative audit records, export/deletion workflow evidence | Security, Compliance, authorized support | Restricted query API, controlled export | Normal application flows cannot mutate accepted audit facts |
| Analytics | Privacy-safe product events, aggregates, reporting models | Product and authorized administration | Event ingestion and analytical queries | Analytics is never authoritative for operational decisions |
| Feature Flags | Flag definitions, targeting rules, rollout state, evaluation audit | Backend, Mobile configuration, Admin | Server-side evaluation API | Security and entitlement enforcement remain in owning domains |

## 4. Data Classes

### 4.1 Authoritative data

Authoritative data represents the current business truth and is writable only by its owning context.

Examples:

- account status;
- story publication state;
- playback progress;
- subscription lifecycle;
- effective entitlement;
- notification preference.

### 4.2 Derived projections

A projection is a read-optimized copy created from APIs or events.

Examples:

- admin account summary;
- search index;
- recommendation feature set;
- unread-notification counter;
- catalog home-page snapshot.

A projection must define:

- source owner;
- update mechanism;
- expected propagation delay;
- rebuild procedure;
- stale-data behavior;
- deletion propagation.

### 4.3 Cache data

Cache data is reconstructable and has an explicit TTL or invalidation strategy.

Redis must not become the only copy of durable business state.

### 4.4 Historical facts

Historical facts may be append-only and immutable.

Examples:

- provider purchase events;
- subscription state transitions;
- administrative audit actions;
- content-publication history;
- security events.

Correction is performed through compensating records, not silent mutation, where the domain requires an auditable history.

### 4.5 Binary assets

Object storage owns binary bytes operationally, while the Media context owns business metadata and lifecycle state.

An object without a valid Media record is orphaned and eligible for controlled cleanup.

## 5. Physical Storage Mapping

| Storage | Intended ownership model |
|---|---|
| PostgreSQL | Module-owned schemas or clearly namespaced tables and migrations |
| Redis | Namespaced keys with explicit owner, TTL, and fallback |
| RabbitMQ | Owner-defined exchanges, routing keys, queues, and event contracts |
| Object storage | Environment and context prefixes with immutable object versions |
| Search index | Derived projection owned by Search or Catalog projection logic |
| Mobile local database | Device-side read model and durable operation queue, never server authority |
| Observability systems | Operational telemetry, not a business system of record |
| Analytics store | Derived privacy-safe analytical data |

## 6. Write Access Rules

A module may write only:

- its own authoritative records;
- its own outbox records;
- its own projections;
- explicitly shared technical infrastructure records with documented ownership.

Forbidden examples:

- Notifications updating subscription state;
- Administration updating Catalog tables directly;
- Listening updating entitlement rows;
- Analytics changing profile data;
- Mobile clients writing publication or subscription state;
- one module modifying another module's Flyway migrations.

Administrative actions must invoke the owning domain use case.

## 7. Read Access Rules

Preferred read mechanisms, in order:

1. local data inside the owning context;
2. synchronous public module interface;
3. dedicated API;
4. purpose-built projection;
5. asynchronous event-fed read model;
6. controlled export for reporting or compliance.

Direct SQL reads across context boundaries are prohibited except for a documented temporary migration or emergency diagnostic procedure approved by architecture and data owners.

## 8. Cross-Context References

Contexts store stable foreign identifiers rather than importing another context's entity model.

Example:

```text
ListeningProgress
- accountId
- profileId
- storyId
- episodeId
- positionMs
```

The Listening context stores identifiers needed for its invariant but does not own the referenced account, profile, story, or episode.

Cross-context database foreign keys may be avoided when they obstruct extraction. Referential correctness is then protected through validated commands, events, reconciliation, and monitoring.

## 9. Consistency Expectations

| Data relationship | Consistency expectation |
|---|---|
| Account disabled → new authentication denied | Immediate or near-immediate |
| Subscription revoked → premium entitlement removed | Strict bounded delay with alerting |
| Story published → search and recommendations updated | Eventual consistency |
| Profile deleted → downstream personal data cleanup | Eventual, tracked workflow |
| Notification read state | Immediate within Notifications |
| Analytics aggregation | Eventual and non-blocking |
| Cache invalidation | Bounded staleness defined per cache |

Security and revenue-sensitive revocations require tighter propagation targets than discovery or analytics updates.

## 10. Deletion and Privacy Propagation

Deletion requests are coordinated workflows, not uncontrolled cascading SQL across contexts.

Each owner must define:

- records to delete;
- records to anonymize;
- records retained for legal or financial reasons;
- child-data handling;
- derived projections to purge;
- cache invalidation;
- object deletion;
- completion event;
- reconciliation procedure.

The Privacy Worker tracks completion by context and records auditable outcomes.

## 11. Backup and Recovery Ownership

Infrastructure teams operate backup systems, but domain owners define recovery correctness.

Each context must document:

- critical tables and objects;
- recovery-point objective;
- recovery-time objective;
- consistency dependencies;
- reconciliation steps after restore;
- external-provider evidence needed for recovery.

Restoring PostgreSQL without reconciling RabbitMQ, Redis, object storage, and provider callbacks may produce inconsistent state and must be handled explicitly.

## 12. Extraction Impact

When a module is extracted into a service:

1. its authoritative tables move under independent ownership;
2. cross-module SQL access is removed;
3. public interfaces become network contracts where required;
4. events and APIs are versioned;
5. data migration is reversible or recoverable;
6. projections are rebuilt or reconnected;
7. security and audit controls remain intact;
8. observability identifies the new deployment boundary.

The ownership in this matrix remains unchanged unless a separate ADR changes it.

## 13. Review Checklist

For every new entity or table:

- Which context owns it?
- Is it authoritative, derived, cached, historical, or binary metadata?
- Who may write it?
- Who needs to read it?
- What is the approved access mechanism?
- What is the consistency requirement?
- What is the retention policy?
- How is deletion propagated?
- How is it backed up and restored?
- Can it be extracted without cross-context SQL?
- Does it contain parent or child personal data?

## 14. Governance

Changes to ownership require review from:

- the current owner;
- the proposed owner;
- architecture;
- security or privacy when sensitive data is involved;
- DevOps when physical storage or recovery changes.

Significant ownership changes require an ADR.

## 15. Related Documents

- `../Architecture_Principles.md`
- `../Database_Design.md`
- `../Backend_Architecture.md`
- `../Event_Catalog.md`
- `../API_Specification.md`
- `08_Architecture_Decision_Guide.md`
- `10_Diagram_Maintenance_Guide.md`
- `16_Known_Technical_Debt.md`
