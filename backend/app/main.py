"""FastAPI Back-end"""

from contextlib import asynccontextmanager
from typing import Any, Dict, List

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from modules.paths import MODEL_PATH, STATIC_DIR, TEMPLATES_DIR, verify_paths
from ai.inference import predict_image

# Verify necessary paths exist from modules package
verify_paths()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Lifespan event to load the model at startup
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Preload ML assets during app startup."""
    from ai.inference import get_model

    get_model(MODEL_PATH)
    yield


# Create FastAPI app with lifespan event
app = FastAPI(title="ARC FastAPI", lifespan=lifespan)

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


# Define root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Render the landing page with placeholder context."""

    context = _base_context(request)
    return templates.TemplateResponse("index.html", context)


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
        return templates.TemplateResponse("index.html", context)

    try:
        prediction = predict_image(file_bytes, MODEL_PATH)
    except ValueError as exc:
        context = _base_context(
            request,
            messages=[_message(str(exc), "error")],
            uploaded_filename=file1.filename,
        )
        return templates.TemplateResponse("index.html", context)

    success_message = _message("Prediction completed successfully.", "success")
    context = _base_context(
        request,
        prediction=prediction["display_label"],
        probability=prediction["confidence"],
        prediction_made=True,
        messages=[success_message],
        uploaded_filename=file1.filename,
    )
    return templates.TemplateResponse("index.html", context)


# Run the app with Uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
