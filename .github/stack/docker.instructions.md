---
description: 'Docker conventions and guidelines.'
applyTo: '**/Dockerfile,**/Dockerfile.*,**/*.dockerfile,**/docker-compose*.yml,**/docker-compose*.yaml'
---

# Docker Guidelines

## Philosophy
Small, secure, reproducible. Nothing unnecessary. Deterministic builds, zero secrets, easy rollback.

## Core Standards
1. **Multi-stage builds** (unless single-file script with no build tooling)
2. **Pinned minimal base** (exact version; never `latest`)
3. **Dependencies before source** to leverage cache
4. **Aggressive `.dockerignore`** (VCS, docs, build outputs, tests, logs, IDE files, secrets)
5. **Combine RUN commands**; clean caches in same layer
6. **Non-root user**; least privilege
7. **No secrets baked in** (never copy .env, never commit credentials)
8. **Exec-form entrypoint** (`CMD` or `ENTRYPOINT` as JSON array)

## Build Discipline
- Order: base → system deps → dependency manifest install → app source → build → runtime stage
- Frequent changes go last
- Final image: runtime assets only

## Configuration
- Runtime config via environment variables or mounted secrets
- Provide safe defaults; validate required vars early and fail fast

## Security
- Minimal base, non-root, scan vulnerabilities, restrict capabilities
- Explicit port declarations at runtime (never rely on implicit exposure)

## Tagging & Reproducibility
- Immutable tags; never patch running containers
- CalVer (`YY.MM.PATCH`)
- `dev` tag for development images (e.g. `echo-backend:dev`)
- Never use `latest` as a build target

## Troubleshooting
- **Image bloat** → Remove tools from final stage; verify multi-stage; check layer history
- **Slow rebuilds** → Reorder Dockerfile; shrink context; cache dependencies
- **Permission errors** → Fix ownership before switching user
- **Secret leak** → Inspect build context + history; rotate credentials immediately

## Checklist
- [ ] Multi-stage build (or justified exception)
- [ ] Version-pinned minimal base
- [ ] `.dockerignore` present and comprehensive
- [ ] Dependency layer cached
- [ ] No superfluous packages in final image
- [ ] Non-root user defined
- [ ] No secrets/env files/VCS metadata
- [ ] Exec-form startup command
- [ ] CI scans for vulnerabilities
- [ ] Immutable tags (CalVer)
- [ ] `dev` tag for dev images
- [ ] Resource limits defined