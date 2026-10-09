# ADR-0012: Flyway Database Migration Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Backend Engineering

## Context

KidsAudioBookPlatform uses PostgreSQL as its primary system of record. Schema changes must be reproducible across local, test, staging, and production environments while preserving data, supporting rolling deployments, and preventing application replicas from racing to modify the database.

The platform contains multiple bounded contexts that may initially share one PostgreSQL cluster while retaining explicit ownership of their tables, indexes, constraints, views, and migration history. Database evolution therefore requires both technical tooling and strict operational rules.

## Decision

Use Flyway for versioned, forward-only database migrations.

Migration scripts are committed with the code that requires them, validated in CI, and executed as a controlled deployment step before incompatible application behavior is enabled. Application instances must not independently compete to apply production migrations during normal startup.

Flyway is the authoritative source of schema history. Hibernate schema auto-update is disabled outside disposable local experiments.

## Migration Types

### Versioned migrations

Versioned migrations are used for permanent schema changes such as:

- tables;
- columns;
- constraints;
- indexes;
- sequences;
- enum or lookup data required by the application;
- ownership and permission changes;
- one-time deterministic data transformations.

Naming convention:

```text
V<version>__<short_description>.sql
```

Example:

```text
V1_3_0__create_story_progress_table.sql
```

Version numbers must be monotonically increasing inside the repository migration history. Teams must avoid renumbering migrations after they have been merged or applied to a shared environment.

### Repeatable migrations

Repeatable migrations use the `R__` prefix and are permitted only for replaceable database objects whose complete definition is safe to reapply, such as:

- views;
- materialized-view definitions;
- stored routines where explicitly approved;
- database-level reporting helpers.

Repeatable migrations must not hide irreversible business-data transformations.

### Operational data jobs

Large backfills, media metadata repairs, or long-running transformations are not embedded blindly in schema migrations. They use dedicated, observable jobs when they could:

- exceed deployment time limits;
- lock large tables;
- create excessive replication lag;
- require pause, resume, or progress tracking;
- need business-level retry and reconciliation.

## Ownership

Each bounded context owns its database migration files and the schema objects they create.

Rules:

1. A module may not alter another module's tables without review from the owning context.
2. Shared infrastructure objects require explicit architecture ownership.
3. Migration paths must make ownership visible through folder structure, schema naming, or documented conventions.
4. Cross-context foreign keys require deliberate lifecycle analysis and architecture approval.
5. Reporting objects must not become an undocumented write path into another context.

## Core Rules

1. Applied versioned migrations are immutable.
2. Every migration must be deterministic.
3. Migration scripts must run successfully on a clean database.
4. Migration scripts must also be valid when upgrading from every supported production schema state.
5. Destructive changes use expand-and-contract.
6. Migrations must not depend on application replica startup order.
7. Production migration execution has one controlled owner.
8. Secrets, environment-specific credentials, and production-only identifiers are never hard-coded.
9. SQL statements must be reviewed for lock duration, table scans, data volume, and rollback implications.
10. Every migration must have a clear reason linked to the feature, defect, or ADR that requires it.

## Expand-and-Contract Strategy

Incompatible changes are split across multiple releases.

### Expand

1. Add the new table, column, index, or representation.
2. Keep the old representation operational.
3. Deploy code capable of writing both forms where required.
4. Ensure old application instances remain compatible during rolling deployment.

### Migrate

1. Backfill existing data with an observable process.
2. Validate row counts, checksums, nullability, referential integrity, and business invariants.
3. Monitor performance and replication impact.
4. Stop or throttle the process when operational thresholds are exceeded.

### Contract

1. Switch all readers to the new representation.
2. Stop writing the old representation.
3. Confirm supported application versions no longer depend on it.
4. Remove obsolete columns, tables, indexes, or code in a later release.

A destructive contract migration must never be deployed in the same step that first introduces the replacement representation.

## Lock and Performance Safety

Potentially expensive operations require explicit review.

Examples include:

- adding a non-null column with an immediate full-table rewrite;
- creating indexes on large active tables;
- validating large constraints;
- changing column types;
- updating every row in a high-volume table;
- rebuilding frequently accessed views;
- changing primary or foreign keys.

The migration plan must consider:

- expected row count;
- estimated runtime;
- lock mode and duration;
- transaction-log growth;
- replication lag;
- connection-pool pressure;
- maintenance-window requirements;
- safe cancellation behavior.

Production-safe techniques such as staged nullability, concurrent indexing where supported, bounded batches, and delayed constraint validation are preferred.

## Transaction Boundaries

Migrations should use transactions when PostgreSQL and the operation support them safely. A large migration must not use one enormous transaction merely for convenience if that creates unacceptable locks, log growth, or rollback cost.

Non-transactional operations must be clearly documented and designed so that partial completion is detectable and recoverable.

## Deployment Sequence

The default production sequence is:

1. Build and validate the release artifact.
2. Back up or confirm recoverability requirements.
3. Run Flyway validation.
4. Execute approved migrations through a dedicated deployment job.
5. Verify schema version and migration checksums.
6. Run migration smoke checks and critical data-integrity checks.
7. Deploy application instances compatible with the new schema.
8. Enable dependent features only after health verification.

Migration failure blocks traffic cutover for the dependent release.

## Validation in CI

CI must:

- apply the full migration history to an empty PostgreSQL database;
- run Flyway validation;
- execute repository integration tests;
- test upgrades from supported baseline snapshots when practical;
- detect duplicate versions and checksum changes;
- validate required indexes and constraints through integration tests;
- reject accidental Hibernate schema generation as a substitute for migrations.

## Testing Requirements

Migration-related changes require tests appropriate to the risk:

- clean-install test;
- supported-version upgrade test;
- data-preservation test;
- compatibility test with old and new application behavior;
- backfill idempotency test;
- constraint and index verification;
- performance rehearsal for high-risk migrations;
- failure and restart test for operational data jobs.

## Rollback and Recovery

Database rollback is not based on automatically reversing arbitrary SQL.

Recovery uses one or more of:

- forward corrective migration;
- application rollback while the expanded schema remains compatible;
- disabling the affected feature through configuration or feature flags;
- restoring from backup for severe data-loss or corruption incidents;
- replaying audited business events or reconciliation jobs where designed.

Before a destructive migration, the deployment plan must define the recovery point, restoration procedure, expected recovery time, and verification steps.

## Observability and Audit

Production migration execution must record:

- migration version and description;
- artifact or commit reference;
- environment;
- start and completion timestamps;
- executor identity;
- duration;
- success or failure;
- affected schema;
- operational notes for high-risk migrations.

Long-running data jobs expose progress, error count, retry count, throughput, estimated remaining work, and last processed cursor.

## Security

Migration credentials follow least privilege. The runtime application account should not automatically inherit every schema-management permission required by the deployment account.

Migration scripts must not log or materialize secrets, authentication tokens, raw child data, or provider credentials.

## Consequences

### Positive

- Reproducible environments.
- Auditable schema history.
- Safer rolling deployments.
- Explicit ownership of database evolution.
- Better protection against accidental data loss.
- Reliable local and CI environment creation.

### Negative

- Requires careful compatibility planning.
- Applied mistakes require corrective migrations.
- Long-running changes need operational coordination.
- Expand-and-contract temporarily increases code and schema complexity.
- Upgrade testing adds CI and maintenance cost.

## Rejected Alternatives

### Hibernate automatic schema updates

Rejected because they provide insufficient control, auditability, compatibility planning, and production safety.

### Manual production SQL

Rejected because it is not reproducible, is difficult to review, and creates hidden divergence between environments.

### Editing historical migrations

Rejected because it invalidates checksums and breaks consistency between environments that applied different content under the same version.

### Automatic down migrations for every change

Rejected because many business-data and PostgreSQL operations are not safely reversible without explicit recovery design.

## Follow-up Actions

- Configure Flyway validation in backend CI.
- Define the repository migration folder convention per bounded context.
- Disable production Hibernate schema mutation.
- Add a deployment migration job with auditable output.
- Create a checklist for high-risk and destructive migrations.
- Add migration compatibility tests before the first production release.
