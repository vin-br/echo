"""YOLOv8 fine-tuning engine for brain tumor object detection."""

import logging
import shutil
from pathlib import Path
from typing import Any

from ultralytics import YOLO

from vision.common.paths import DETECTION_DATASET, MODELS_DIR, RESULTS_DIR
from vision.common.config import DEVICE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_DETECTION_MODELS_DIR = MODELS_DIR / "detection"

# Default training hyperparameters
DEFAULTS: dict[str, Any] = {
    "model": "yolov8n.pt",
    "epochs": 100,
    "imgsz": 640,
    "batch": 16,
    "lr0": 0.01,
    "patience": 15,
    "device": str(DEVICE),
}


def _resolve_model(model: str) -> str:
    """Resolve a YOLO model name to models/detection/.

    If a short name like 'yolov8n.pt' is given, check models/detection/ first.
    If found there, use it; otherwise let YOLO download it, then move it.
    """
    model_path = Path(model)

    # Already an absolute path — use as-is
    if model_path.is_absolute():
        return model

    target = _DETECTION_MODELS_DIR / model_path.name
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        return str(target)

    # Let YOLO download via short name, then move to models/detection/
    logger.info("Downloading %s to %s", model, target)
    YOLO(model)  # triggers download to CWD
    downloaded = Path(model)
    if downloaded.exists():
        shutil.move(str(downloaded), str(target))

    return str(target)


def train(
    *,
    model: str = DEFAULTS["model"],
    epochs: int = DEFAULTS["epochs"],
    imgsz: int = DEFAULTS["imgsz"],
    batch: int = DEFAULTS["batch"],
    lr0: float = DEFAULTS["lr0"],
    patience: int = DEFAULTS["patience"],
    device: str = DEFAULTS["device"],
    data_yaml: Path | None = None,
    project: Path | None = None,
    name: str | None = None,
) -> Path:
    """Fine-tune a YOLOv8 model on the brain tumor detection dataset.

    Parameters
    ----------
    model : str
        Pre-trained YOLO model name or path (e.g. 'yolov8n.pt', 'yolov8s.pt').
    epochs : int
        Maximum training epochs.
    imgsz : int
        Input image size (pixels).
    batch : int
        Batch size.
    lr0 : float
        Initial learning rate.
    patience : int
        Early stopping patience (epochs without improvement).
    device : str
        Training device ('cpu', '0', 'mps').
    data_yaml : Path | None
        Path to dataset YAML. Defaults to data/detection/data.yaml.
    project : Path | None
        Output project directory. Defaults to vision/results/detection.
    name : str | None
        Run name. Auto-generated if None.

    Returns
    -------
    Path
        Path to the best model weights.
    """
    data_yaml = data_yaml or DETECTION_DATASET / "data.yaml"
    project = project or RESULTS_DIR / "detection"

    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset config not found: {data_yaml}")

    if name is None:
        base = Path(model).stem
        name = f"{base}-e{epochs}-b{batch}-img{imgsz}"

    logger.info("Training YOLO: model=%s epochs=%d batch=%d imgsz=%d", model, epochs, batch, imgsz)

    resolved_model = _resolve_model(model)
    yolo = YOLO(resolved_model)
    yolo.train(
        data=str(data_yaml),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        lr0=lr0,
        patience=patience,
        device=device,
        project=str(project),
        name=name,
        exist_ok=True,
        verbose=True,
    )

    # Copy best weights to models/ for the backend to pick up
    best_weights = project / name / "weights" / "best.pt"
    if best_weights.exists():
        dest = _DETECTION_MODELS_DIR / "yolo-brain-tumor.pt"
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, dest)
        logger.info("Best weights copied to %s", dest)

    return best_weights
