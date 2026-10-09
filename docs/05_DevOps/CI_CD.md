# Continuous Integration and Delivery

Version: 2.0.0  
Status: Required release pipeline design  
Owner: DevOps and Engineering

## 1. Pipeline objective

Every source change must produce attributable test results and immutable artifacts. Protected branches reject unreviewed changes and failing quality gates. Production receives only artifacts already tested in staging.

## 2. Required pull-request checks

| Stage | Evidence |
|---|---|
| Repository hygiene | Formatting, license/secret scan, protected-branch policy |
| Backend build | Java 21 compilation, Maven dependency checks |
| Backend tests | JUnit unit + Testcontainers integration + architecture checks |
| API and schemas | OpenAPI/schema lint + consumer compatibility checks |
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

Git SHA and artifact digest identify every deployment. Retain logs, approval record, migration version, changelog and rollback decision.

## 4. Release control

- Use least-privilege GitHub environments and OIDC/workload identity where provider supports it.
- No long-lived production tokens in repository variables.
- Require manual approval for production promotions and protected deployment environments.
- Feature flags allow independent activation; flags must have owner and removal date.
- Database schema uses backward-compatible expand/migrate/contract.
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

Adjust paths/workflows to actual monorepo modules. Pin action SHAs in production workflows. Flutter, admin, container, scan and deployment jobs are required additions, not implied by the example above.

## 7. Traceability and metrics

Track lead time, deployment frequency, failed-deployment rate, time-to-restore, flaky tests, pipeline duration, artifact provenance and critical vulnerability age. Never optimize pipeline speed by removing child-safety checks.

Related: [Deployment](Deployment.md), [Testing Strategy](../06_Testing/Testing_Strategy.md), [Git Workflow](../04_Engineering/Git_Workflow.md).
