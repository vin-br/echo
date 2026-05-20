FROM python:3.14.5-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies using intermediate layer for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=vision/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=vision/uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project

# Copy vision training code
COPY vision ./vision/

# Bake in models
COPY models/ ./models/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Keep container alive for manual training commands
CMD ["sleep", "infinity"]
