"""PyTorch Functions for Model Training."""

import json
import logging
import math
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from models.config import DEVICE, IMAGENET_MEAN, IMAGENET_STD, NUM_CLASSES, MODEL_REGISTRY
from modules.paths import CHECKPOINTS_DIR, LOGS_DIR, RESULTS_DIR

# Keep runs deterministic for reproducibility.
torch.manual_seed(42)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _format_lr_label(lr: float) -> str:
    """Format learning rate using scientific notation without zero padding."""

    if lr <= 0:
        raise ValueError("Learning rate must be positive for checkpoint naming.")
    exponent = math.floor(math.log10(lr))
    mantissa = lr / (10**exponent)
    mantissa_str = ("{:.4g}".format(mantissa)).rstrip("0").rstrip(".")
    return f"{mantissa_str}e{exponent}"


def _display_progress(message: str) -> None:
    """Log and print training progress so notebooks show live updates."""

    logger.info(message)
    print(message)


def _compose_transforms(image_size: int, augment: bool, normalize: bool) -> transforms.Compose:
    """Create a torchvision transform pipeline.

    Parameters
    ----------
    image_size : int
        Final square resolution fed to the network.
    augment : bool
        Whether to enable lightweight spatial augmentation.
    normalize : bool
        Apply ImageNet normalization statistics after tensor conversion.

    Returns
    -------
    transforms.Compose
        Sequential operations applied to every sample.
    """
    ops: list[Callable] = [transforms.Resize((image_size, image_size))]
    if augment:
        ops.append(transforms.RandomHorizontalFlip())
    ops.append(transforms.ToTensor())
    if normalize:
        ops.append(transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD))
    return transforms.Compose(ops)


def _build_loader(
    directory: Path,
    image_size: int,
    batch_size: int,
    shuffle: bool,
    augment: bool = False,
    normalize: bool = True,
) -> DataLoader:
    """Instantiate a DataLoader for an image directory tree.

    Parameters
    ----------
    directory : Path
        Root folder following ImageFolder expectations.
    image_size : int
        Target resolution for every sample.
    batch_size : int
        Number of items per batch.
    shuffle : bool
        Whether to reshuffle each epoch.
    augment : bool, optional
        Apply augmentation transforms, by default False.
    normalize : bool, optional
        Apply ImageNet normalization after tensor conversion, by default True.

    Returns
    -------
    DataLoader
        Loader yielding `(images, labels)` batches.
    """
    dataset = datasets.ImageFolder(
        directory, transform=_compose_transforms(image_size, augment, normalize)
    )
    return DataLoader(
        dataset, batch_size=batch_size, shuffle=shuffle, num_workers=0, pin_memory=False
    )


def build_dataloaders(
    train_dir: Path,
    val_dir: Path,
    test_dir: Path,
    image_size: int,
    batch_size: int,
    augment: bool = True,
    normalize: bool = True,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Build train/validation/test loaders with consistent settings.

    Parameters
    ----------
    train_dir : Path
        Directory containing the training split.
    val_dir : Path
        Directory containing the validation split.
    test_dir : Path
        Directory containing the testing split.
    image_size : int
        Resolution shared by every split.
    batch_size : int
        Batch size applied to every loader.
    augment : bool, optional
        Whether to apply augmentation on the training split, by default True.
    normalize : bool, optional
        Apply ImageNet normalization across all splits, by default True.

    Returns
    -------
    tuple[DataLoader, DataLoader, DataLoader]
        Train, validation, and test loaders in that order.
    """
    train_loader = _build_loader(
        train_dir, image_size, batch_size, True, augment=augment, normalize=normalize
    )
    val_loader = _build_loader(val_dir, image_size, batch_size, False, normalize=normalize)
    test_loader = _build_loader(test_dir, image_size, batch_size, False, normalize=normalize)
    return train_loader, val_loader, test_loader


def train_one_epoch(
    model: nn.Module, loader: DataLoader, criterion: nn.Module, optimizer: Adam
) -> Tuple[float, float]:
    """Execute a single optimization epoch.

    Parameters
    ----------
    model : nn.Module
        Model being optimized.
    loader : DataLoader
        Loader that yields training samples.
    criterion : nn.Module
        Loss function.
    optimizer : Adam
        Optimizer that applies gradient updates.

    Returns
    -------
    tuple[float, float]
        Average loss and accuracy for this epoch.
    """
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for images, labels in loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()  # Reset gradients from the previous step.
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()  # Standard backwards pass.
        optimizer.step()  # Apply the gradient update.

        running_loss += loss.item() * images.size(0)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        total += labels.size(0)

    return running_loss / total, correct / total


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module) -> Tuple[float, float]:
    """Run inference on a loader without gradient tracking.

    Parameters
    ----------
    model : nn.Module
        Model evaluated in eval mode.
    loader : DataLoader
        Loader that yields validation or test batches.
    criterion : nn.Module
        Loss function applied during evaluation.

    Returns
    -------
    tuple[float, float]
        Average loss and accuracy produced by the loader.
    """
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            outputs = model(images)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * images.size(0)  # Scale by batch for true mean.
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

    return running_loss / total, correct / total


def run_experiment(
    name: str,
    model_builder: Callable[[], nn.Module],
    train_dir: Path,
    val_dir: Path,
    test_dir: Path,
    image_size: int,
    batch_size: int,
    epochs: int,
    lr: float = 1e-4,
    augment: bool = True,
    normalize: bool = True,
) -> Dict[str, Any]:
    """Full training routine used by the notebook experiments.

    Parameters
    ----------
    name : str
        Label printed each epoch.
    model_builder : Callable[[], nn.Module]
        Factory returning a pretrained feature extractor with a custom head.
    train_dir : Path
        Directory for the training split.
    val_dir : Path
        Directory for the validation split.
    test_dir : Path
        Directory for the testing split.
    image_size : int
        Resolution applied to every sample.
    batch_size : int
        Batch size shared across splits.
    epochs : int
        Number of training epochs.
    lr : float, optional
        Learning rate for Adam, by default 1e-4. The best-performing weights
        are automatically saved to the shared ``MODELS_DIR`` using run metadata
        for the filename so they can be loaded later without additional setup.
    augment : bool, optional
        Enable light data augmentation on the training split, by default True.
    normalize : bool, optional
        Apply ImageNet normalization after converting to tensors, by default True.

    Returns
    -------
    Dict[str, Any]
        History, metrics, the trained model, and checkpoint path.
    """
    safe_name = name.replace(" ", "-")
    lr_label = _format_lr_label(lr)
    checkpoint_name = f"{safe_name}-b{batch_size}-img{image_size}-e{epochs}-lr-{lr_label}"

    checkpoint_path = CHECKPOINTS_DIR / f"{checkpoint_name}.pt"
    log_path = LOGS_DIR / f"{checkpoint_name}.log"
    results_path = RESULTS_DIR / f"{checkpoint_name}.json"

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    try:
        train_loader, val_loader, test_loader = build_dataloaders(
            train_dir,
            val_dir,
            test_dir,
            image_size,
            batch_size,
            augment=augment,
            normalize=normalize,
        )
        model = model_builder()
        criterion = nn.CrossEntropyLoss()
        optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr)

        history = {"train_acc": [], "val_acc": []}
        best_state = deepcopy(model.state_dict())
        best_val_acc = 0.0
        best_record = {"epoch": 1, "train_acc": 0.0, "val_acc": 0.0}

        for epoch in range(1, epochs + 1):
            _, train_acc = train_one_epoch(model, train_loader, criterion, optimizer)
            _, val_acc = evaluate(model, val_loader, criterion)

            history["train_acc"].append(train_acc)
            history["val_acc"].append(val_acc)

            progress_message = (
                f"[{name}] epoch {epoch}/{epochs} train_acc={train_acc:.4f} val_acc={val_acc:.4f}"
            )
            _display_progress(progress_message)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_state = deepcopy(model.state_dict())
                best_record = {"epoch": epoch, "train_acc": train_acc, "val_acc": val_acc}

        model.load_state_dict(best_state)
        torch.save(best_state, checkpoint_path)

        val_loss, val_acc = evaluate(model, val_loader, criterion)
        test_loss, test_acc = evaluate(model, test_loader, criterion)

        summary_message = (
            f"[{name}] best={best_record['epoch']}/{epochs} val={best_record['val_acc']:.4f}\n"
            f"[{name}] final val={val_acc:.4f} test={test_acc:.4f}\n"
        )

        _display_progress(summary_message)

        experiment_result: Dict[str, Any] = {
            "history": history,
            "val_metrics": {"loss": val_loss, "acc": val_acc},
            "test_metrics": {"loss": test_loss, "acc": test_acc},
            "model": model,
            "checkpoint_path": checkpoint_path,
            "log_path": log_path,
            "results_path": results_path,
            "best_epoch": best_record["epoch"],
            "best_epoch_metrics": {
                "train_acc": best_record["train_acc"],
                "val_acc": best_record["val_acc"],
            },
            "config": {
                "name": name,
                "image_size": image_size,
                "batch_size": batch_size,
                "epochs": epochs,
                "lr": lr,
                "augment": augment,
                "normalize": normalize,
                "train_dir": str(train_dir),
                "val_dir": str(val_dir),
                "test_dir": str(test_dir),
            },
        }

        json_ready = {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in experiment_result.items()
            if key != "model"
        }
        with results_path.open("w", encoding="utf-8") as fp:
            json.dump(json_ready, fp, indent=2)

        return experiment_result
    finally:
        logger.removeHandler(file_handler)
        file_handler.close()


def build_model(name: str) -> nn.Module:
    cfg = MODEL_REGISTRY[name]
    model = cfg["factory"](weights=cfg["weights"])
    for param in model.parameters():
        param.requires_grad = False
    head = model
    for segment in cfg["head_path"][:-1]:
        head = getattr(head, segment)
    last = cfg["head_path"][-1]
    layer = head[last] if isinstance(last, int) else getattr(head, last)
    in_features = layer.in_features
    new_layer = nn.Linear(in_features, NUM_CLASSES)
    if isinstance(last, int):
        head[last] = new_layer
    else:
        setattr(head, last, new_layer)
    return model.to(DEVICE)


__all__ = [
    "run_experiment",
    "build_model",
]
