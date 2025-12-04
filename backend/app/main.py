"""FastAPI Back-end Migration."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from .load_model import get_model
from modules.paths import STATIC_DIR, TEMPLATES_DIR, verify_paths

# Verify necessary paths exist from modules package
verify_paths()

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Lifespan event to load the model at startup
@asynccontextmanager
async def lifespan(_: FastAPI):
    """Preload ML assets during app startup."""
    # get_model()
    yield


# Create FastAPI app with lifespan event
app = FastAPI(title="ARC FastAPI", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Define root endpoint
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request) -> HTMLResponse:
    """Render the landing page with placeholder context."""
    context = {
        "request": request,
        "prediction": None,
        "probability": None,
        "prediction_made": False,
        "annotated_image": None,
        "yolo": False,
        "messages": [],
    }
    return templates.TemplateResponse("index.html", context)


# Run the app with Uvicorn if executed directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
