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

# Copy application code
COPY backend ./backend
COPY modules ./modules
COPY frontend ./frontend
COPY models/checkpoints/convnext-tiny-b16-img224-e60-lr-5e-4.pt ./models/checkpoints/convnext-tiny-b16-img224-e60-lr-5e-4.pt

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
