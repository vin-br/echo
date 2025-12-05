"""Utilities to run single-image predictions for the FastAPI service."""

import io
import re
from typing import Dict, cast

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

from models.config import CLASS_LABELS, DEVICE, IMAGENET_MEAN, IMAGENET_STD
from modules.paths import MODEL_PATH

from .load_model import get_model

_DEFAULT_IMAGE_SIZE = 224
_IMAGE_SIZE_PATTERN = re.compile(r"img(?P<size>\d+)")


def _infer_image_size() -> int:
    match = _IMAGE_SIZE_PATTERN.search(MODEL_PATH.name.lower())
    if match:
        return int(match.group("size"))
    return _DEFAULT_IMAGE_SIZE


_IMAGE_SIZE = _infer_image_size()
_TRANSFORM = transforms.Compose(
    [
        transforms.Resize((_IMAGE_SIZE, _IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ]
)


def _load_image(file_bytes: bytes) -> Image.Image:
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Please upload a valid PNG or JPEG image.") from exc
    return image


def _format_label(label: str) -> str:
    return label.replace("_", " ").title()


def predict_image(file_bytes: bytes) -> Dict[str, float | str]:
    """Run a forward pass on the uploaded image and return the results."""

    image = _load_image(file_bytes)
    tensor = _TRANSFORM(image)
    # Some type checkers infer the transform result as a PIL Image; cast to torch.Tensor
    tensor = cast(torch.Tensor, tensor)
    tensor = tensor.unsqueeze(0).to(DEVICE)

    model = get_model()
    with torch.no_grad():
        logits = model(tensor)
        probabilities = torch.softmax(logits, dim=1)
        confidence, predicted_idx = torch.max(probabilities, dim=1)

    label = CLASS_LABELS[int(predicted_idx.item())]
    return {
        "label": label,
        "display_label": _format_label(label),
        "confidence": float(confidence.item() * 100),
    }


__all__ = ["predict_image"]
