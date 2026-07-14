# ADR-0012: Flyway Database Migration Strategy

- Status: Accepted
- Date: 2026-07-14
- Decision Owners: Architecture and Backend Engineering

## Context

The platform uses PostgreSQL as the primary system of record. Schema changes must be reproducible across local, test, staging, and production environments while preserving data and supporting rolling deployments.

## Decision

Use Flyway for versioned, forward-only database migrations. Migration scripts are committed with the code that requires them and run automatically during controlled deployment.

## Naming Convention

```text
V<version>__<short_description>.sql
```

Example:

```text
V1_3_0__create_story_progress_table.sql
```

Repeatable migrations may be used only for database views or replaceable routines where that behavior is explicitly appropriate.

## Rules

1. Applied versioned migrations are immutable.
2. Every migration must be deterministic and safe to rerun through environment recreation.
3. Destructive changes use an expand-and-contract process.
4. Large data backfills are separated from schema changes when they could block deployment.
5. Indexes on large tables should use production-safe techniques and be evaluated for lock impact.
6. Migrations must not depend on application startup order across multiple replicas.
7. Each bounded context owns its schema migrations.

## Expand-and-Contract

For incompatible changes:

1. Add the new column, table, or representation.
2. Deploy code that can read or write both representations where required.
3. Backfill existing data.
4. Switch all readers and writers.
5. Remove the obsolete structure in a later release.

## Validation

CI creates a clean database and applies the complete migration history. Integration tests validate upgrades from a supported previous schema version. Production deployments must fail before application traffic is switched when migration validation fails.

## Rollback

Database rollback is not based on automatically reversing arbitrary SQL. Recovery uses forward corrective migrations, application rollback compatible with the expanded schema, or restore procedures for severe incidents.

## Consequences

### Positive

- Reproducible environments.
- Auditable schema history.
- Safer collaboration and deployment.
- Clear ownership of database evolution.

### Negative

- Requires careful compatibility planning.
- Applied mistakes require corrective migrations.
- Long-running migrations need operational coordination.

## Rejected Alternatives

- Hibernate automatic schema updates: insufficient control and auditability.
- Manual production SQL: not reproducible.
- Editing historical migrations: breaks environment consistency.