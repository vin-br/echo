"""Backend path constants."""

from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = _APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

BACKEND_DATA_DIR = BACKEND_DIR / "data"
BACKEND_DATA_DIR.mkdir(exist_ok=True)

MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "classification" / "convnext-tiny-b16-img224-e150-lr-8_823e-3.pt"

VISION_DIR = PROJECT_ROOT / "vision"
RESULTS_DIR = VISION_DIR / "results"


def verify_paths(skip_files: bool = False) -> None:
    """Ensure core directories/files exist before depending on them."""
    required_dirs = {"BACKEND_DIR": BACKEND_DIR}
    required_files = {"MODEL_PATH": MODEL_PATH}

    missing = []
    for name, path in required_dirs.items():
        if not path.is_dir():
            missing.append(f"{name} -> {path}")

    if not skip_files:
        for name, path in required_files.items():
            if not path.is_file():
                missing.append(f"{name} -> {path}")

    if missing:
        details = "\n - ".join(missing)
        raise FileNotFoundError(
            "Missing required project paths:\n - " + details
        )
