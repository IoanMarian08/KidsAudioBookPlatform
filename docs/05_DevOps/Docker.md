# Docker Image Standards

Version: 2.0.0  
Status: Engineering baseline  
Owner: Backend and DevOps

## 1. Objectives

Build deterministic, reasonably small, non-root OCI images for Java 21 Spring Boot API and workers. Images are immutable artifacts; staging and production deploy the same digest with environment-specific secrets/configuration.

## 2. Build rules

- Pin builder/runtime image by tested major version and ideally digest; regularly refresh security patches.
- Multi-stage build; do not ship Maven cache, JDK compiler or source tree unnecessarily.
- Use .dockerignore for .git, build output, IDE directories, secrets and archives.
- Never pass secrets as Docker build args that become layer history; use a secure build-secret mechanism.
- Run as dedicated non-root UID/GID; restrict filesystem to read-only when the app supports it.
- Define sensible memory/CPU limits and graceful termination behavior.
- Scan image and its dependencies before promotion; store SBOM and provenance.

## 3. Illustrative Java 21 image

~~~dockerfile
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /workspace
COPY pom.xml .
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
RUN groupadd -g 10001 app && useradd -u 10001 -g app -r app
COPY --from=build /workspace/target/*.jar app.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
~~~

This is a starting template only. Actual module names, Maven modules, artifact paths and base image tags must match the repository and chosen runtime OS. Production pipeline must run tests before building this image. Pin image digests and ensure the preferred base supports the shell/user tooling used above.

## 4. Runtime health and termination

Use Spring Boot actuator health endpoints with separated liveness/readiness roles. Liveness reports process health, readiness reports ability to serve critical requests; neither should expose credentials. Graceful shutdown must stop accepting requests, allow in-flight HTTP work and ensure workers finish/return unacknowledged jobs within a finite window.

## 5. JVM and container memory

Set container resources first; size JVM heap to leave headroom for metaspace, native buffers, threads and GC. Observe real metrics and tune only after load tests. Container OOM is a deployment defect even if heap metrics appear normal.

## 6. Image naming, provenance and storage

Tag with immutable Git SHA, build timestamp and semantic release where applicable. Deploy by digest rather than floating latest tags. Sign artifacts if infrastructure supports it; block promotion on critical vulnerabilities unless documented exception with expiry and owner exists.

## 7. Security checklist

[ ] Base image audited / supported  
[ ] Non-root process  
[ ] No secrets in build context or image layers  
[ ] Runtime ports only  
[ ] Read-only filesystem where feasible  
[ ] SBOM and scans retained  
[ ] Resource limits + health probes  
[ ] Reproducible build and rollback digest

Related: [Docker Compose](Docker_Compose.md), [CI/CD](CI_CD.md), [Security Architecture](../03_Architecture/Security_Architecture.md).
