"""FastAPI Back-end"""

import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from shared.paths import (
    MODEL_PATH,
    STATIC_DIR,
    TEMPLATES_DIR,
    RESULTS_DIR,
    BACKEND_DATA_DIR,
    verify_paths,
)
from backend.app.inference import predict_image
from backend.app.database import MetricsDatabase

# Verify necessary paths exist from modules package
# Skip file verification in CI environment where models don't exist
verify_paths(skip_files=os.getenv("CI") is not None)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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
    title="AI Radiology Copilot - ARC API",
    description="API for an AI assistant to classify brain tumor images using deep learning models",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # enforce 25 MB cap without middleware


def _base_context(request: Request, **overrides: Any) -> Dict[str, Any]:
    context = {
        "request": request,
        "prediction": None,
        "probability": None,
        "prediction_made": False,
        "annotated_image": None,
        "yolo": False,
        "messages": [],
        "uploaded_filename": None,
        "uploaded_image": None,
    }
    context.update(overrides)
    return context


def _message(text: str, level: str = "info") -> Dict[str, str]:
    return {"text": text, "level": level}


# Health check endpoint
@app.get("/healthz")
async def healthz() -> Dict[str, str]:
    """Health check endpoint for Docker healthcheck."""
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def _favicon() -> Response:
    """Return empty response for favicon requests to avoid 404 log spam."""
    return Response(status_code=204)


# Define root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Render the landing page with placeholder context."""

    context = _base_context(request)
    return templates.TemplateResponse(request, "index.html", context)


@app.post("/", response_class=HTMLResponse)
async def classify_image(request: Request, file1: UploadFile = File(...)) -> HTMLResponse:
    """Accept an uploaded image and display the model prediction."""

    file_bytes = await file1.read()
    messages: List[Dict[str, str]] = []
    if not file1.filename:
        messages.append(_message("Please select an image before submitting.", "error"))
    elif len(file_bytes) == 0:
        messages.append(_message("The uploaded file was empty.", "error"))
    elif len(file_bytes) > MAX_UPLOAD_BYTES:
        messages.append(_message("Image exceeds the 25 MB limit.", "error"))
    if messages:
        context = _base_context(
            request,
            messages=messages,
            uploaded_filename=file1.filename,
        )
        return templates.TemplateResponse(request, "index.html", context)

    try:
        prediction = predict_image(file_bytes, MODEL_PATH)
    except ValueError as exc:
        context = _base_context(
            request,
            messages=[_message(str(exc), "error")],
            uploaded_filename=file1.filename,
        )
        return templates.TemplateResponse(request, "index.html", context)

    import base64
    uploaded_image_b64 = base64.b64encode(file_bytes).decode("utf-8")
    success_message = _message("Prediction completed", "success")
    context = _base_context(
        request,
        prediction=prediction["display_label"],
        probability=prediction["confidence"],
        prediction_made=True,
        messages=[success_message],
        uploaded_filename=file1.filename,
        uploaded_image=uploaded_image_b64,
    )
    return templates.TemplateResponse(request, "index.html", context)


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
