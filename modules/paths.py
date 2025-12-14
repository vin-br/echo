"""Project-wide path constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Backend directories
BACKEND_DIR = PROJECT_ROOT / "backend"

# Frontend directories
FRONTEND_DIR = PROJECT_ROOT / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

# AI Service and Models directories
AI_DIR = PROJECT_ROOT / "ai"
RESULTS_DIR = AI_DIR / "results"
LOGS_DIR = AI_DIR / "logs"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "convnext-tiny-b16-img224-e60-lr-5e-4.pt"

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
TRAINING_DATASET = DATA_DIR / "training"
TESTING_DATASET = DATA_DIR / "testing"


def verify_paths() -> None:
    """Ensure core directories/files exist before depending on them."""
    required_dirs = {
        "PROJECT_ROOT": PROJECT_ROOT,
        "BACKEND_DIR": BACKEND_DIR,
        "FRONTEND_DIR": FRONTEND_DIR,
        "TEMPLATES_DIR": TEMPLATES_DIR,
        "STATIC_DIR": STATIC_DIR,
    }
    required_files = {
        "MODEL_PATH": MODEL_PATH,
    }

    missing = []
    for name, path in required_dirs.items():
        if not path.is_dir():
            missing.append(f"{name} -> {path}")

    for name, path in required_files.items():
        if not path.is_file():
            missing.append(f"{name} -> {path}")

    if missing:
        details = "\n - ".join(missing)
        raise FileNotFoundError(
            "Missing required project paths. Create the expected structure before continuing:\n"
            f" - {details}"
        )


__all__ = [
    "PROJECT_ROOT",
    "BACKEND_DIR",
    "FRONTEND_DIR",
    "TEMPLATES_DIR",
    "STATIC_DIR",
    "AI_DIR",
    "MODELS_DIR",
    "RESULTS_DIR",
    "LOGS_DIR",
    "MODEL_PATH",
    "DATA_DIR",
    "TRAINING_DATASET",
    "TESTING_DATASET",
    "verify_paths",
]
