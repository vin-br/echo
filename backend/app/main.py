"""FastAPI Back-end — API"""

import os
import time
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response

from backend.app.paths import (
    MODEL_PATH,
    RESULTS_DIR,
    BACKEND_DATA_DIR,
    verify_paths,
)
from backend.app.inference import predict_image
from backend.app.database import MetricsDatabase

# Verify necessary paths exist
verify_paths(skip_files=os.getenv("CI") is not None)

# Global database instance
database: Optional[MetricsDatabase] = None


# Lifespan event to load the model at startup
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Preload ML assets during app startup."""
    global database
    from backend.app.inference import get_model

    get_model(MODEL_PATH)

    # Initialize database and ingest all JSON results
    database_path = BACKEND_DATA_DIR / "metrics.duckdb"
    database = MetricsDatabase(database_path)

    # Ingest all existing JSON files
    for json_file in RESULTS_DIR.glob("*.json"):
        database.ingest_json(json_file)

    yield

    database.close()


# Create FastAPI app with lifespan event
app = FastAPI(
    title="ARC API",
    description="API to augment, recognize and classify brain tumor images using deep learning models",
    version="26.05.1",
    docs_url="/docs",  # Swagger UI
    lifespan=lifespan,
)

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # enforce 25 MB cap


# Health check endpoint
@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    """Health check endpoint for Docker healthcheck."""
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def _favicon() -> Response:
    """Return empty response for favicon requests to avoid 404 log spam."""
    return Response(status_code=204)


@app.post("/api/predict")
async def predict(file1: UploadFile = File(...)) -> Dict[str, Any]:
    """Accept an uploaded image and return the model prediction as JSON."""
    file_bytes = await file1.read()

    if not file1.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file was empty")
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="Image exceeds the 25 MB limit")

    try:
        start = time.perf_counter()
        result = predict_image(file_bytes, MODEL_PATH)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if database is not None:
            database.record_latency(elapsed_ms)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return {
        "prediction": result["display_label"],
        "confidence": result["confidence"],
        "inference_ms": round(elapsed_ms, 1),
    }


@app.get("/api/latency")
async def get_latency() -> Dict[str, Any]:
    """Return rolling average inference latency from recent predictions."""
    if database is None:
        return {"avg_ms": None, "count": 0}
    return database.get_latency()


@app.get("/api/metrics")
async def get_metrics() -> List[Dict[str, Any]]:
    """Generic metrics endpoint (same data as /api/metrics for now)."""
    if database is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    return database.get_metrics()


# Run the app with Uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
