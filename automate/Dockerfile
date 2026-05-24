FROM python:3.14.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app/automate

ENV UV_PROJECT_ENVIRONMENT=/usr/local \
    UV_COMPILE_BYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Install Firefox + system deps as root into /ms-playwright (world-readable)
RUN playwright install --with-deps firefox \
    && apt-get install -y --no-install-recommends fonts-liberation fonts-noto-core \
    && chmod -R o+rX /ms-playwright \
    && rm -rf /var/lib/apt/lists/*

COPY automate.py .

# Non-root user — can read /ms-playwright thanks to the chmod above
RUN useradd -m -u 1000 app && chown -R app:app /app
USER app

ENTRYPOINT ["python", "automate.py"]
CMD ["all"]
