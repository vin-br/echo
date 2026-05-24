"""Vision service path constants."""

from pathlib import Path

VISION_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = VISION_DIR.parent

MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = VISION_DIR / "results"
LOGS_DIR = VISION_DIR / "logs"

DATA_DIR = PROJECT_ROOT / "data"

# Classification dataset (folder-per-class)
TRAINING_DATASET = DATA_DIR / "classification" / "train"
TESTING_DATASET = DATA_DIR / "classification" / "test"

# Detection dataset (YOLO format)
DETECTION_DATASET = DATA_DIR / "detection"
