"""ML constants for model training and evaluation."""

import torch
from torchvision import models

DEVICE = torch.device("cpu")

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

CLASS_LABELS = (
    "glioma_tumor",
    "meningioma_tumor",
    "no_tumor",
    "pituitary_tumor",
)

NUM_CLASSES = len(CLASS_LABELS)

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
