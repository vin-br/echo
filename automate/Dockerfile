FROM python:3.14.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app/automate

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Install Firefox, Playwright system deps, and fonts for proper rendering
RUN .venv/bin/playwright install --with-deps firefox \
    && apt-get install -y --no-install-recommends \
       fonts-liberation fonts-noto-core \
    && fc-cache -f \
    && rm -rf /var/lib/apt/lists/*

COPY automate.py .

ENTRYPOINT [".venv/bin/python", "automate.py"]
CMD ["all"]
