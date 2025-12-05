"""Minimal utilities for loading a PyTorch model once."""

from pathlib import Path

import torch
from torch import nn

from models.config import MODEL_REGISTRY
from modules.paths import MODEL_PATH
from models.trainer import build_model

DEFAULT_MODEL_KEY = "convnext-tiny"

_MODEL: nn.Module | None = None


def _detect_model_key(path: Path) -> str:
    """Infer the model registry key from the checkpoint filename."""

    name = path.stem.lower()
    for key in MODEL_REGISTRY:
        if key in name:
            return key
    return DEFAULT_MODEL_KEY


def _load_model(path: Path) -> nn.Module:
    """Load a serialized PyTorch model from disk and switch to eval mode."""

    try:
        scripted = torch.jit.load(str(path), map_location="cpu")
    except (RuntimeError, ValueError, FileNotFoundError):
        scripted = None

    if isinstance(scripted, nn.Module):
        scripted.eval()
        return scripted

    checkpoint = torch.load(path, map_location="cpu")
    if isinstance(checkpoint, nn.Module):
        checkpoint.eval()
        return checkpoint
    if isinstance(checkpoint, dict):
        model_key = _detect_model_key(path)
        model = build_model(model_key)
        model.load_state_dict(checkpoint)
        model.eval()
        return model
    raise TypeError("MODEL_PATH must point to a serialized torch.nn.Module or state dict.")


def get_model() -> nn.Module:
    """Return the cached PyTorch model, loading it on first access."""
    global _MODEL
    if _MODEL is None:
        _MODEL = _load_model(MODEL_PATH)
    return _MODEL
