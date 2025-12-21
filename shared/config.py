"""Setting up constants for model training and evaluation."""

import torch

from torchvision import models

# Device type set to CPU for compatibility
DEVICE = torch.device("cpu")

# Normalization stats from ImageNet pretraining to keep pixel values in the
# distribution expected by torchvision's pretrained weights.
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# Canonical class labels used across training, evaluation, and serving.
CLASS_LABELS = (
    "glioma_tumor",
    "meningioma_tumor",
    "no_tumor",
    "pituitary_tumor",
)

# Mapping from class index to label
# CLASS_INDEX_TO_LABEL = {idx: label for idx, label in enumerate(CLASS_LABELS)}
# Mapping from class label to index
# CLASS_LABEL_TO_INDEX = {label: idx for idx, label in enumerate(CLASS_LABELS)}
NUM_CLASSES = len(CLASS_LABELS)

# Registry of available model architectures with their constructors and pretrained weights
MODEL_REGISTRY = {
    "resnet50": {
        "factory": models.resnet50,
        "weights": models.ResNet50_Weights.IMAGENET1K_V2,
        "head_path": ("fc",),
    },
    "mobilenet-v3-large": {
        "factory": models.mobilenet_v3_large,
        "weights": models.MobileNet_V3_Large_Weights.IMAGENET1K_V1,
        "head_path": ("classifier", 3),
    },
    "convnext-tiny": {
        "factory": models.convnext_tiny,
        "weights": models.ConvNeXt_Tiny_Weights.IMAGENET1K_V1,
        "head_path": ("classifier", 2),
    },
}

__all__ = [
    "DEVICE",
    "IMAGENET_MEAN",
    "IMAGENET_STD",
    "CLASS_LABELS",
    # "CLASS_INDEX_TO_LABEL",
    # "CLASS_LABEL_TO_INDEX",
    "NUM_CLASSES",
    "MODEL_REGISTRY",
]
