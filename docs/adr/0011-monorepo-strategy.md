# ADR-0011: Monorepo over Git Submodules

## Status
Accepted

## Date
2026-07-16

## Context
The Nexus platform consists of 5 components:
- `backend/` — FastAPI + PostgreSQL
- `frontend/` — Admin web UI (React/Vue)
- `mobile/ios/` — iOS SwiftUI app
- `mobile/android/` — Android Kotlin app
- Root — Docker Compose, CI/CD, shared config, docs

The initial AGENTS.md specified a **git submodule** architecture (each component is a separate git repo). Before implementation begins, we must decide whether to keep submodules or switch to a monorepo.

Key constraints:
- Small team (potentially solo developer)
- AI-driven development via orchestrator + specialist agents
- Early stage: everything changes frequently
- Shared contracts: API changes affect backend, frontend, and mobile simultaneously

## Decision
**Switch to monorepo.** All components live in a single git repository. Each component remains a self-contained directory with its own build system, dependencies, and tests — but shares the same git history.

```
Nexus/                     # Single git repo (this is it)
├── backend/               # FastAPI (uv, ruff, mypy, pytest)
├── frontend/              # React/Vue (npm/vite)
├── mobile/
│   ├── ios/               # SwiftUI (SPM, Swift Testing)
│   └── android/           # Kotlin (Gradle, Hilt)
├── docs/                  # ADRs, contracts, architecture
├── docker-compose.yml     # Shared infrastructure
├── Makefile               # Unified dev commands
└── .github/               # CI/CD, agents, skills
```

## Rationale

### 1. AI Agent Effectiveness
Agents (orchestrator, code-reviewer, api-designer, etc.) operate on the workspace. In a submodule setup, they can only see ONE submodule at a time. In a monorepo, the orchestrator can:
- Verify API contracts match backend + iOS + Android implementations in one pass
- Run the code-reviewer across all layers
- Ensure a backend schema change is reflected in mobile DTOs

### 2. Atomic Cross-Component Changes
API contract changes are the most common cross-cutting change. In a monorepo:
```
commit: feat(appointments): add recurrence field
  backend/app/appointments/schemas.py     # Pydantic schema
  mobile/ios/.../Appointment.swift        # iOS model
  mobile/android/.../Appointment.kt       # Android model
  docs/contracts/appointments.yaml        # Contract update
```
One commit, one PR, one review. In submodules: 3-4 separate PRs across repos.

### 3. Simplified CI/CD
One `.github/workflows/` directory runs everything:
- `ci-backend.yml` — only triggers on `backend/**` changes
- `ci-ios.yml` — only triggers on `mobile/ios/**` changes
- `ci-android.yml` — only triggers on `mobile/android/**` changes
- `ci-integration.yml` — triggers on any change, runs cross-component tests

GitHub Actions path filters make this efficient — no rebuild of everything on every commit.

### 4. Developer Experience
| Operation | Submodules | Monorepo |
|---|---|---|
| Clone | `git clone --recursive` (pray) | `git clone` |
| Pull latest | `git pull && git submodule update` | `git pull` |
| Branch | One branch per repo | One branch for the feature |
| PR | Multiple PRs, coordinate merge order | One PR |
| Bisect | Nightmare (which submodule commit?) | `git bisect` works |

### 5. When Submodules Would Be Better
If Nexus grows to the point where:
- 3+ independent teams own different components
- Different release cadences are needed (mobile releases weekly, backend releases daily)
- External contributors only work on one component

...then extracting a component to its own repo is straightforward: `git subtree split` preserves history.

## Consequences

### Positive
- AI agents can see the entire codebase in one workspace
- Cross-component changes are atomic (one commit)
- Single CI/CD configuration with path-based triggers
- Simplified onboarding: `git clone`, `make up`, done
- `git bisect` and `git blame` work across the entire project
- No submodule sync issues, detached HEAD, or `.gitmodules` merge conflicts

### Negative
- Repository will grow large over time (mitigated by shallow clones and sparse checkout if needed)
- No independent versioning per component (mitigated by path-filtered CI and separate changelogs per component)
- Merge conflicts may span backend + mobile (rare, and better than inconsistent submodule pins)

### Mitigations
- Use `CODEOWNERS` with path-based ownership if multiple people join
- Path-filtered GitHub Actions (`paths: [backend/**]`) prevents unnecessary CI runs
- Each component keeps its own `CHANGELOG.md` for release notes
- If a component grows enough to warrant independent releases, extract it via `git subtree split`

## Alternatives Considered

| Alternative | Rejected Because |
|---|---|
| Git Submodules | AI agents can't cross-reference; atomic changes impossible; clone/pull UX is painful |
| Git Subtree | Still separate repos; merge direction confusion; tooling is esoteric |
| Polyrepo (no meta-repo) | No shared docker-compose, CI, or contracts; coordination overhead |
| Nx/Turborepo | Overkill for a 5-component project; adds build system complexity we don't need yet |

## Migration
Since we haven't initialized submodules yet, no migration is needed. Simply:
1. Remove `.gitmodules` if it exists
2. Remove any `git submodule` references from documentation
3. Update AGENTS.md architecture section
4. All directories (`backend/`, `mobile/`, `frontend/`) are already part of this repo
