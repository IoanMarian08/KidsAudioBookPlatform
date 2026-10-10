# Continuous Integration and Delivery

Version: 2.0.0  
Status: Required release pipeline design  
Owner: DevOps and Engineering

## 1. Pipeline objective

Every source change must produce attributable test results and immutable artifacts **for each independently built/deployed microservice**. Java services have separate build/test/image/migration units, while cross-service contracts and security journeys are validated together. Protected branches reject unreviewed changes and failing quality gates. Production receives only artifacts already tested in staging.

## 2. Required pull-request checks

| Stage | Evidence |
|---|---|
| Repository hygiene | Formatting, license/secret scan, protected-branch policy |
| Service builds | Build affected Java 21/Spring Boot microservices separately, plus shared technical libraries |
| Per-service tests | JUnit unit, service-owned PostgreSQL Testcontainers integration and forbidden cross-service dependency checks |
| Cross-service contracts | OpenAPI consumer/provider compatibility + versioned RabbitMQ event schemas and idempotency/ordering checks |
| Flutter | Analyze/format/test, widget/golden/a11y checks where configured |
| Admin dashboard | Lint/build/test when module exists |
| Security | SAST, SCA, secrets, container vulnerabilities, SBOM |
| Infrastructure | Docker build and IaC validation/plan |
| Docs | Markdown links, ADR/PRD contract sync and Mermaid syntax review |

Do not skip tests through merge labels without a time-limited, approved exception.

## 3. Promotion stages

~~~mermaid
flowchart LR
    PR[PR checks] --> Merge[Protected branch]
    Merge --> Build[Immutable build + SBOM]
    Build --> Stage[Deploy staging]
    Stage --> Verify[Smoke + E2E + security/perf gates]
    Verify --> Approval[Release approval]
    Approval --> Prod[Canary/rolling prod]
    Prod --> Observe[SLO and alert watch]
    Observe -->|failure| Rollback[Rollback to prior digest]
~~~

Git SHA **plus each service's artifact digest** identifies a deployment. A release can deploy one service without rebuilding/redeploying other services. Retain per-service logs, approval, contract versions, Flyway database revision and rollback decision.

## 4. Release control

- Use least-privilege GitHub environments and OIDC/workload identity where provider supports it.
- No long-lived production tokens in repository variables.
- Require manual approval for production promotions and protected deployment environments.
- Feature flags allow independent activation; flags must have owner and removal date.
- **Each owning service** manages its own Flyway migrations and backward-compatible expand/migrate/contract; no service deploy may modify another service's database.
- Migration down scripts are not assumed safe; tested forward fix may be the preferred recovery.
- New mobile features must tolerate older app versions and delayed store rollouts.

## 5. Failure policies

Compilation, security-critical findings, schema incompatibility, acceptance failures and missing production readiness evidence block promotion. Flaky tests require quarantined issue/owner and tracked cleanup, never blanket disablement. Retry external dependency fetches only with bounded attempts.

## 6. Suggested GitHub Actions outline

~~~yaml
name: quality-gates
on:
  pull_request:
  push:
    branches: [main]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - run: mvn -B verify
~~~

The YAML above is a **generic illustration**, not a deployable multi-service CI pipeline. The actual repository must implement a matrix/paths-based build per `services/*-service`, with each service's Maven tests, image digest, security/SBOM scan and integration tests. Include contract verification against peers, gateway routing smoke, cross-service E2E, and independent staging/prod promotion for every service. Pin action SHAs in production workflows.

## 7. Traceability and metrics

Track lead time, deployment frequency, failed-deployment rate, time-to-restore, flaky tests, pipeline duration, artifact provenance and critical vulnerability age. Never optimize pipeline speed by removing child-safety checks.

Related: [Deployment](Deployment.md), [Testing Strategy](../06_Testing/Testing_Strategy.md), [Git Workflow](../04_Engineering/Git_Workflow.md).
