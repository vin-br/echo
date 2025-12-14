"""Inference utilities for loading models and making predictions."""

import io
import re
from pathlib import Path
from typing import Dict, cast

import torch
from PIL import Image, UnidentifiedImageError
from torch import nn
from torchvision import transforms

from ai.config import CLASS_LABELS, DEVICE, IMAGENET_MEAN, IMAGENET_STD, MODEL_REGISTRY
from ai.trainer import build_model

_DEFAULT_IMAGE_SIZE = 224
_IMAGE_SIZE_PATTERN = re.compile(r"img(?P<size>\d+)")

# Cached model instance
_MODEL: nn.Module | None = None
_CURRENT_MODEL_PATH: Path | None = None


def _detect_model_key(path: Path) -> str:
    """Infer the model registry key from the checkpoint filename."""
    name = path.stem.lower()
    for key in MODEL_REGISTRY:
        if key in name:
            return key
    # Default to first available model
    return list(MODEL_REGISTRY.keys())[0]


def _infer_image_size(model_path: Path) -> int:
    """Extract image size from model filename (e.g., 'img224' -> 224)."""
    match = _IMAGE_SIZE_PATTERN.search(model_path.name.lower())
    if match:
        return int(match.group("size"))
    return _DEFAULT_IMAGE_SIZE


def load_model(model_path: Path) -> nn.Module:
    """Load a PyTorch model from checkpoint and set to eval mode."""
    global _MODEL, _CURRENT_MODEL_PATH

    # Return cached model if already loaded
    if _MODEL is not None and _CURRENT_MODEL_PATH == model_path:
        return _MODEL

    # Try loading as TorchScript first
    try:
        scripted = torch.jit.load(str(model_path), map_location=DEVICE)
        if isinstance(scripted, nn.Module):
            scripted.eval()
            _MODEL = scripted
            _CURRENT_MODEL_PATH = model_path
            return scripted
    except (RuntimeError, ValueError, FileNotFoundError):
        pass

    # Load as state dict
    checkpoint = torch.load(model_path, map_location=DEVICE, weights_only=True)

    if isinstance(checkpoint, nn.Module):
        checkpoint.eval()
        _MODEL = checkpoint
        _CURRENT_MODEL_PATH = model_path
        return checkpoint

    if isinstance(checkpoint, dict):
        model_key = _detect_model_key(model_path)
        model = build_model(model_key)
        model.load_state_dict(checkpoint)
        model.eval()
        _MODEL = model
        _CURRENT_MODEL_PATH = model_path
        return model

    raise TypeError(f"Checkpoint at {model_path} must be a torch.nn.Module or state dict.")


def get_model(model_path: Path) -> nn.Module:
    """Get cached model or load it on first access."""
    global _MODEL
    if _MODEL is None:
        _MODEL = load_model(model_path)
    return _MODEL


def _load_image(file_bytes: bytes) -> Image.Image:
    """Load and validate image from bytes."""
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except UnidentifiedImageError as exc:
        raise ValueError("Please upload a valid PNG or JPEG image.") from exc
    return image


def _format_label(label: str) -> str:
    """Format label for display (e.g., 'glioma_tumor' -> 'Glioma Tumor')."""
    return label.replace("_", " ").title()


def predict_image(file_bytes: bytes, model_path: Path) -> Dict[str, float | str]:
    """Run inference on uploaded image and return prediction results."""

    # Load image and prepare transform
    image = _load_image(file_bytes)
    image_size = _infer_image_size(model_path)

    transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
        ]
    )

    # Prepare input tensor
    tensor = transform(image)
    tensor = cast(torch.Tensor, tensor)  # Type hint for checkers
    tensor = tensor.unsqueeze(0).to(DEVICE)

    # Run inference
    model = get_model(model_path)
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


__all__ = ["load_model", "get_model", "predict_image"]
