"""Vision service path constants."""

from pathlib import Path

VISION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = VISION_DIR.parent

MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = VISION_DIR / "results"
LOGS_DIR = VISION_DIR / "logs"

DATA_DIR = PROJECT_ROOT / "data"
TRAINING_DATASET = DATA_DIR / "training"
TESTING_DATASET = DATA_DIR / "testing"
