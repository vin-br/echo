"""Tumor detection and annotation using YOLOv8.

Uses a fine-tuned YOLOv8 model to predict bounding boxes around tumour
regions in brain MRI scans.  The model outputs [x1, y1, x2, y2] boxes
that are drawn on the image with OpenCV's drawing API to produce an
annotated image returned as a base64 PNG.
"""

import base64
import logging
import os

os.environ.setdefault("YOLO_AUTOINSTALL", "false")

import cv2
import numpy as np
from typing import Any

from backend.app.paths import MODELS_DIR

logger = logging.getLogger(__name__)

YOLO_MODEL_PATH = MODELS_DIR / "detection" / "yolo-brain-tumor.pt"

# BGR colour palette for OpenCV drawing — muted medical tones
COLORS: dict[str, tuple] = {
    "Glioma Tumor":     (100, 100, 230),  # Soft red
    "Meningioma Tumor": (100, 180, 230),  # Soft amber
    "Pituitary Tumor":  (200, 180, 100),  # Soft teal
    "No Tumor":         (150, 200, 130),  # Soft sage
}

# ── YOLO detection ──────────────────────────────────────────────────────

_yolo_model: Any = None

# Minimum confidence for a YOLO detection to be drawn.
_YOLO_CONF = 0.15


def _get_yolo() -> Any | None:
    """Load and cache the YOLOv8 model.  Returns None when the weights file is missing."""
    global _yolo_model
    if _yolo_model is not None:
        return _yolo_model
    if not YOLO_MODEL_PATH.exists():
        logger.warning("YOLO model not found at %s", YOLO_MODEL_PATH)
        return None
    from ultralytics import YOLO
    _yolo_model = YOLO(str(YOLO_MODEL_PATH))
    logger.info("YOLO model loaded from %s", YOLO_MODEL_PATH)
    return _yolo_model


def _detect_yolo(image: np.ndarray) -> list[list[int]]:
    """Run YOLOv8 inference and return bounding boxes in xyxy format."""
    model = _get_yolo()
    if model is None:
        return []
    results = model(image, verbose=False, conf=_YOLO_CONF)
    return [
        box.xyxy[0].cpu().numpy().astype(int).tolist()
        for r in results for box in r.boxes
    ]


# ── Annotation ──────────────────────────────────────────────────────────

def _annotate(
    image: np.ndarray,
    boxes: list[list[int]],
    label: str,
    confidence: float,
) -> np.ndarray:
    """Draw bounding boxes and labels on the image."""
    out = image.copy()
    color = COLORS.get(label, (200, 200, 200))
    text = f"{label} {confidence:.0f}%"

    for x1, y1, x2, y2 in boxes:
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 1)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        label_y = max(y1, th + 8)
        cv2.rectangle(out, (x1, label_y - th - 6), (x1 + tw + 8, label_y + 2), color, -1)
        cv2.putText(
            out, text, (x1 + 4, label_y - 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA,
        )
    return out


def _stamp_message(image: np.ndarray, message: str, color: tuple) -> np.ndarray:
    """Overlay a status message at the top of the image."""
    out = image.copy()
    cv2.putText(
        out, message, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA,
    )
    return out


# ── Public API ──────────────────────────────────────────────────────────

def detect_and_annotate(
    image_bytes: bytes, label: str, confidence: float,
) -> dict[str, Any]:
    """Full detection + annotation pipeline.

    Returns dict with:
      - annotated_image : base64 PNG string
      - detections      : number of bounding boxes found
      - method          : "yolo", "none", or "unavailable"
      - message         : human-readable status (only when no boxes drawn)
    """
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image for detection")

    message: str | None = None

    if label == "No Tumor":
        annotated = _stamp_message(image, "No Tumor Detected", COLORS["No Tumor"])
        boxes: list[list[int]] = []
        method = "none"
    elif _get_yolo() is None:
        annotated = _stamp_message(
            image, "Detection model unavailable", (130, 130, 200),
        )
        boxes = []
        method = "unavailable"
        message = "YOLO detection model is not loaded. Ensure yolo-brain-tumor.pt is present."
    else:
        boxes = _detect_yolo(image)
        method = "yolo"
        if boxes:
            annotated = _annotate(image, boxes, label, confidence)
        else:
            annotated = _stamp_message(
                image, "No region detected", COLORS.get(label, (200, 200, 200)),
            )
            message = "The model could not precisely locate the tumor in this scan."

    _, buffer = cv2.imencode(".png", annotated)
    result: dict[str, Any] = {
        "annotated_image": base64.b64encode(buffer).decode("utf-8"),
        "detections": len(boxes),
        "method": method,
    }
    if message:
        result["message"] = message
    return result
