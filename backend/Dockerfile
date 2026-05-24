FROM python:3.14.5-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies (no dev deps in production)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

# Copy application code
COPY backend ./backend/

# Bake model checkpoints into image
COPY models/classification/convnext-tiny-b16-img224-e150-lr-8_823e-3.pt ./models/classification/convnext-tiny-b16-img224-e150-lr-8_823e-3.pt
COPY models/detection/yolo-brain-tumor.pt ./models/detection/yolo-brain-tumor.pt

# Copy training results (metrics JSON + plot HTML for leaderboard & carousel)
COPY vision/results ./vision/results/

EXPOSE 8000

# Non-root user
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz').read()" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
