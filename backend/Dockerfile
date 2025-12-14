FROM python:3.14.1-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Copy poetry files for installing dependencies
COPY backend/pyproject.toml backend/poetry.lock ./

# Install poetry and dependencies using lock file
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-ansi --no-root --only main && \
    rm -rf /root/.cache/pip

# Copy application directories
COPY backend ./backend/
COPY frontend ./frontend/
COPY modules ./modules/

# Copy AI inference files
COPY ai/config.py ./ai/config.py
COPY ai/inference.py ./ai/inference.py  
COPY ai/trainer.py ./ai/trainer.py

# Copy model checkpoint
COPY models/convnext-tiny-b16-img224-e60-lr-5e-4.pt ./models/convnext-tiny-b16-img224-e60-lr-5e-4.pt

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz').read()" || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
