FROM python:3.14.2-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies using intermediate layer for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=ai/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=ai/uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project

# Copy AI training code and shared modules
COPY ai ./ai/
COPY shared ./shared/

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import sys; sys.exit(0)" || exit 1

# Keep container alive for manual training commands
CMD ["sleep", "infinity"]
