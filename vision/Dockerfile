# ── Builder ──────────────────────────────────────────────────────────
FROM python:3.14.5-slim AS builder

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=vision/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=vision/uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# ── Runtime ──────────────────────────────────────────────────────────
FROM python:3.14.5-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Merge only site-packages (skip venv bin/ to keep the base image python intact)
COPY --from=builder /opt/venv/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/

# Copy vision training code
COPY vision ./vision/

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python3 -c "import sys; sys.exit(0)" || exit 1

# Keep container alive for manual training commands
CMD ["sleep", "infinity"]
