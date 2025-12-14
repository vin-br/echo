FROM python:3.14.1-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy poetry files for installing dependencies
COPY ai/pyproject.toml ./

# Install poetry and dependencies using lock file
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-ansi --no-root --only main && \
    rm -rf /root/.cache/pip

# Copy AI training code and shared modules
COPY ai ./ai/ \
     modules ./modules/

# Note: models/ and data/ are mounted via docker-compose volumes

EXPOSE 8001

# Default command for training (can be overridden in docker-compose)
CMD ["python", "-m", "ai.train"]
