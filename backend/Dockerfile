FROM python:3.14.2-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies using intermediate layer for caching
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# Copy application directories
COPY backend ./backend/
COPY frontend ./frontend/
COPY shared ./shared/

# Copy model checkpoint
COPY models/convnext-tiny-b16-img224-e60-lr-5e-4.pt ./models/convnext-tiny-b16-img224-e60-lr-5e-4.pt

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz').read()" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
