"""ML constants for model inference."""

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
    "convnext-small": {
        "factory": models.convnext_small,
        "weights": models.ConvNeXt_Small_Weights.IMAGENET1K_V1,
        "head_path": ("classifier", 2),
    },
    "efficientnet-v2-s": {
        "factory": models.efficientnet_v2_s,
        "weights": models.EfficientNet_V2_S_Weights.IMAGENET1K_V1,
        "head_path": ("classifier", 1),
    },
    "swin-v2-t": {
        "factory": models.swin_v2_t,
        "weights": models.Swin_V2_T_Weights.IMAGENET1K_V1,
        "head_path": ("head",),
    },
    "maxvit-t": {
        "factory": models.maxvit_t,
        "weights": models.MaxVit_T_Weights.IMAGENET1K_V1,
        "head_path": ("classifier", 5),
    },
}
