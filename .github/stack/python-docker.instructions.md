---
description: 'Python Docker conventions with uv.'
applyTo: '**/Dockerfile,**/Dockerfile.*'
---

# Python Docker with uv

## Philosophy
Fast, minimal, reproducible. System-level installs, multi-stage builds, cached layers.

## Stack
- **Base**: `python:<version>-slim` (pin exact version)
- **uv**: From `ghcr.io/astral-sh/uv:latest`
- **No venv**: Container provides isolation

## Standard Pattern
```dockerfile
FROM python:3.14.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_COMPILE_BYTECODE=1

# Dependencies (cached layer)
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Source code
COPY . .

# Non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

CMD ["python", "-m", "your_module"]
```

## Key Settings
- **`UV_PROJECT_ENVIRONMENT=/usr/local`**: Install to system Python, skip venv
- **`UV_COMPILE_BYTECODE=1`**: Pre-compile for faster startup
- **`--frozen`**: Use exact lockfile versions, fail if stale
- **`--no-dev`**: Exclude dev dependencies
- **Cache mount**: Speeds up repeated builds

## .dockerignore
```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.git/
.env
*.log
```

## Checklist
- [ ] `python:3.14.5-slim` base
- [ ] `UV_PROJECT_ENVIRONMENT=/usr/local`
- [ ] Dependencies cached before source
- [ ] `--frozen --no-dev` flags used
- [ ] Cache mount for uv
- [ ] Non-root user
- [ ] `.venv/` in `.dockerignore`