# Docker Compose for Local Development

Version: 2.0.0  
Status: Reference blueprint, adapt to repo layout  
Owner: Engineering Enablement

## 1. Purpose

Provide a reproducible local stack for backend API, worker, PostgreSQL, Redis, RabbitMQ and MinIO/object storage. Keep all development services local and disposable; no production secrets or customer data.

## 2. Reference services

~~~yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: kids_audio_dev
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?Set dev database password}
    ports: ["127.0.0.1:5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d kids_audio_dev"]
      interval: 5s
      timeout: 3s
      retries: 15

  redis:
    image: redis:7
    ports: ["127.0.0.1:6379:6379"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 15

  rabbitmq:
    image: rabbitmq:3-management
    environment:
      RABBITMQ_DEFAULT_USER: dev
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD:?Set dev broker password}
    ports:
      - "127.0.0.1:5672:5672"
      - "127.0.0.1:15672:15672"
    volumes: ["rabbitdata:/var/lib/rabbitmq"]

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: devminio
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD:?Set dev object password}
    ports:
      - "127.0.0.1:9000:9000"
      - "127.0.0.1:9001:9001"
    volumes: ["miniodata:/data"]

volumes:
  pgdata:
  rabbitdata:
  miniodata:
~~~

This is a local-only example, **not production configuration**. Pin tested image versions/digests before formalizing the Compose file. MinIO bucket bootstrap, API and worker definitions belong in the repository's actual Compose configuration. Environment variable substitutions enforce required development credentials.

## 3. Start/stop workflow

1. Create a local ignored .env from .env.example; use random development passwords.
2. Run docker compose config and inspect substitutions.
3. Run docker compose up -d.
4. Wait for healthy dependencies and apply Flyway migrations.
5. Start API and worker via IDE or local images.
6. Run smoke checks: account -> catalog -> local media object -> playback authorization -> progress sync.
7. Use docker compose down to stop; docker compose down -v **deletes local data** and requires explicit intention.

## 4. Isolation and safety

Bind admin ports to loopback only. Do not reuse credentials across environments. .env must remain gitignored. Billing and push integrations use sandboxes/fakes. Prevent local workers from connecting to real customer queues through misconfigured env vars. Document object URL differences between host browser/mobile emulator/container.

## 5. Testing and troubleshooting

Use Testcontainers for repeatable integration tests instead of relying on a developer's persistent Compose state. Compose exists for exploration/manual debugging. Common problems: port conflict, nonready DB, stale volume schema, broker auth mismatch, emulator unable to resolve localhost, mismatched S3 signing hostnames and Docker resource limits.

**Readiness checklist:** all dependencies healthy, migrations applied, sample story upload/access tested, log correlation working, clean restart preserves only intended volumes.

Related: [Docker](Docker.md), [Infrastructure](Infrastructure.md), [Integration Testing](../06_Testing/Integration_Testing.md).
