---
name: docker
description: "Docker Compose development environment management for Nexus. Use when: starting/stopping services, debugging containers, rebuilding images, checking logs, or modifying docker-compose.yml."
argument-hint: "[task] Docker operation..."
---

# Docker Development Environment

## When to Use
- Starting, stopping, or restarting the full stack
- Rebuilding images after dependency changes
- Debugging container issues (logs, exec, health checks)
- Adding or modifying services in `docker-compose.yml`
- Checking container status, resource usage, or network connectivity

## Stack Overview

```
┌─────────────────────────────────────────┐
│  Traefik (reverse proxy) :80/:443       │
│  ├── api (FastAPI) :8000                │
│  │   ├── postgres :5432                 │
│  │   └── redis :6379                    │
│  ├── pgadmin :5050                      │
│  └── mailpit :8025 (UI) :1025 (SMTP)    │
└─────────────────────────────────────────┘
```

## Commands

```sh
# Start all services (from repo root)
docker compose up -d

# Start with rebuild (after dependency changes)
docker compose up -d --build

# View logs
docker compose logs -f api          # API only
docker compose logs -f --tail=100   # All services, last 100 lines

# Stop everything
docker compose down

# Stop and remove volumes (reset database)
docker compose down -v

# Restart a single service
docker compose restart api

# Execute commands inside a container
docker compose exec api bash
docker compose exec postgres psql -U nexus -d nexus
docker compose exec redis redis-cli

# Check status
docker compose ps
docker stats
```

## Service Endpoints (Dev)

| Service   | URL                       |
|-----------|---------------------------|
| API       | http://localhost:3670      |
| Swagger   | http://localhost:3670/docs |
| pgAdmin   | http://localhost:3673      |
| Mailpit   | http://localhost:3674      |
| Redis     | localhost:3672             |
| Postgres  | localhost:3671             |

## docker-compose.yml Structure Rules
- Root-level `docker-compose.yml` only (no per-submodule compose files)
- Services: `api`, `postgres`, `redis`, `pgadmin`, `mailpit`
- Use named volumes for persistent data (postgres_data, redis_data)
- Health checks on `postgres` and `redis`; `api` depends on both
- Environment variables from `.env` file (never hardcode secrets)
- Ports exposed only for development; Traefik handles routing in production

## Troubleshooting

```sh
# Database connection issues
docker compose exec postgres pg_isready -U nexus

# Redis connectivity
docker compose exec redis redis-cli ping

# API health check
curl http://localhost:8000/health

# Reset everything
docker compose down -v
docker compose up -d --build
```

## Adding a New Service
1. Add the service definition to `docker-compose.yml`
2. If it needs persistence, add a named volume
3. Add health check if it's a dependency for other services
4. Update this skill's "Stack Overview" and "Service Endpoints" sections
5. Run `docker compose up -d <service>` to test
