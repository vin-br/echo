"""PyTorch Functions for Model Training."""

import json
import logging
import math
import os
from copy import deepcopy
from pathlib import Path
from collections.abc import Callable
from typing import Any

import mlflow
import optuna
import torch
from torch import nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader, Subset, TensorDataset
from torchvision import datasets, transforms

from vision.common.config import DEVICE, IMAGENET_MEAN, IMAGENET_STD, NUM_CLASSES, CLASS_LABELS, MODEL_REGISTRY
from vision.common.paths import MODELS_DIR, LOGS_DIR, RESULTS_DIR
from vision.common.visualize import plot_history

# MLflow tracking URI — defaults to local directory, override via env var
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", str(RESULTS_DIR / "mlruns")))

# Keep runs deterministic for reproducibility.
torch.manual_seed(42)

# Number of DataLoader worker processes. More workers keep the GPU fed by
# decoding images in parallel on CPU while the GPU trains. num_workers=0 means
# everything runs on the main thread, starving MPS/CUDA of data.
_NUM_WORKERS = min(6, os.cpu_count() or 1)

# Only CUDA benefits from float16 autocast (dedicated tensor cores). MPS's
# float16 path is incomplete — attention ops and log_softmax silently produce
# NaN or overflow, destabilising ConvNeXt at high LRs.
_USE_AUTOCAST = DEVICE.type == "cuda"
_AUTOCAST_DTYPE = torch.bfloat16 if DEVICE.type == "cpu" else torch.float16


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _format_lr_label(lr: float) -> str:
    """Format learning rate using scientific notation without zero padding."""

    if lr <= 0:
        raise ValueError("Learning rate must be positive for checkpoint naming.")
    exponent = math.floor(math.log10(lr))
    mantissa = lr / (10**exponent)
    mantissa_str = ("{:.4g}".format(mantissa)).rstrip("0").rstrip(".")
    return f"{mantissa_str}e{exponent}".replace(".", "_")


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
        ops.extend([
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(15),
            transforms.RandomAffine(degrees=0, translate=(0.05, 0.05), scale=(0.95, 1.05)),
        ])
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
        dataset, batch_size=batch_size, shuffle=shuffle,
        num_workers=_NUM_WORKERS, pin_memory=False,
        persistent_workers=_NUM_WORKERS > 0,
    )


def build_dataloaders(
    train_dir: Path,
    val_dir: Path,
    test_dir: Path,
    image_size: int,
    batch_size: int,
    augment: bool = True,
    normalize: bool = True,
    val_split: float = 0.2,
) -> tuple[DataLoader, DataLoader, DataLoader]:
    """Build train/validation/test loaders with consistent settings.

    When ``val_dir`` equals ``test_dir`` (no separate validation set), the
    training data is automatically split using ``val_split`` to prevent
    evaluating model selection on the held-out test set (data leakage).

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
    val_split : float, optional
        Fraction of training data to hold out for validation when
        ``val_dir == test_dir``, by default 0.2.

    Returns
    -------
    tuple[DataLoader, DataLoader, DataLoader]
        Train, validation, and test loaders in that order.
    """
    test_loader = _build_loader(test_dir, image_size, batch_size, False, normalize=normalize)

    if val_dir == test_dir and val_split > 0:
        # Split training set into train/val to avoid data leakage
        train_ds = datasets.ImageFolder(
            train_dir, transform=_compose_transforms(image_size, augment, normalize)
        )
        val_ds = datasets.ImageFolder(
            train_dir, transform=_compose_transforms(image_size, False, normalize)
        )
        n = len(train_ds)
        indices = torch.randperm(n, generator=torch.Generator().manual_seed(42)).tolist()
        split = int((1 - val_split) * n)
        train_loader = DataLoader(
            Subset(train_ds, indices[:split]),
            batch_size=batch_size, shuffle=True,
            num_workers=_NUM_WORKERS, pin_memory=False,
            persistent_workers=_NUM_WORKERS > 0,
        )
        val_loader = DataLoader(
            Subset(val_ds, indices[split:]),
            batch_size=batch_size, shuffle=False,
            num_workers=_NUM_WORKERS, pin_memory=False,
            persistent_workers=_NUM_WORKERS > 0,
        )
    else:
        train_loader = _build_loader(
            train_dir, image_size, batch_size, True, augment=augment, normalize=normalize
        )
        val_loader = _build_loader(val_dir, image_size, batch_size, False, normalize=normalize)

    return train_loader, val_loader, test_loader


def train_one_epoch(
    model: nn.Module, loader: DataLoader, criterion: nn.Module, optimizer: torch.optim.Optimizer
) -> tuple[float, float]:
    """Execute a single optimization epoch.

    Parameters
    ----------
    model : nn.Module
        Model being optimized.
    loader : DataLoader
        Loader that yields training samples.
    criterion : nn.Module
        Loss function.
    optimizer : torch.optim.Optimizer
        Optimizer that applies gradient updates.

    Returns
    -------
    tuple[float, float]
        Average loss and accuracy for this epoch.
    """
    model.train()
    # Accumulate on-device to avoid GPU↔CPU sync every batch (major MPS bottleneck).
    running_loss = torch.tensor(0.0, device=DEVICE)
    correct = torch.tensor(0, dtype=torch.long, device=DEVICE)
    total = 0
    for images, labels in loader:
        images = images.to(DEVICE, non_blocking=True)
        labels = labels.to(DEVICE, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.autocast(DEVICE.type, dtype=_AUTOCAST_DTYPE, enabled=_USE_AUTOCAST):
            outputs = model(images)
            loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.detach().float() * images.size(0)
        correct += (outputs.detach().argmax(dim=1) == labels).sum()
        total += labels.size(0)

    # Single sync point per epoch instead of per batch.
    return running_loss.item() / total, correct.item() / total


def evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module) -> tuple[float, float]:
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
    running_loss = torch.tensor(0.0, device=DEVICE)
    correct = torch.tensor(0, dtype=torch.long, device=DEVICE)
    total = 0
    with torch.inference_mode():
        for images, labels in loader:
            images = images.to(DEVICE, non_blocking=True)
            labels = labels.to(DEVICE, non_blocking=True)
            with torch.autocast(DEVICE.type, dtype=_AUTOCAST_DTYPE, enabled=_USE_AUTOCAST):
                outputs = model(images)
                loss = criterion(outputs, labels)

            running_loss += loss.float() * images.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum()
            total += labels.size(0)

    return running_loss.item() / total, correct.item() / total


def _per_class_metrics(model: nn.Module, loader: DataLoader) -> dict[str, Any]:
    """Compute precision, recall, F1 per class and macro F1 on a data loader."""
    model.eval()
    all_preds: list[int] = []
    all_labels: list[int] = []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(DEVICE)
            preds = model(images).argmax(dim=1).cpu().tolist()
            all_preds.extend(preds)
            all_labels.extend(labels.tolist())

    num_classes = NUM_CLASSES
    per_class: dict[str, dict[str, float]] = {}
    f1_scores: list[float] = []

    for cls_idx in range(num_classes):
        tp = sum(1 for p, t in zip(all_preds, all_labels) if p == cls_idx and t == cls_idx)
        fp = sum(1 for p, t in zip(all_preds, all_labels) if p == cls_idx and t != cls_idx)
        fn = sum(1 for p, t in zip(all_preds, all_labels) if p != cls_idx and t == cls_idx)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        label = CLASS_LABELS[cls_idx] if cls_idx < len(CLASS_LABELS) else str(cls_idx)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
        f1_scores.append(f1)

    macro_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0.0

    # Build confusion matrix (row=true, col=predicted)
    cm: list[list[int]] = [[0] * num_classes for _ in range(num_classes)]
    for p, t in zip(all_preds, all_labels):
        cm[t][p] += 1

    return {
        "per_class": per_class,
        "macro_f1": macro_f1,
        "confusion_matrix": cm,
        "class_labels": list(CLASS_LABELS),
    }


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
) -> dict[str, Any]:
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
        Learning rate for AdamW, by default 1e-4. The best-performing weights
        are automatically saved to the shared ``MODELS_DIR`` using run metadata
        for the filename so they can be loaded later without additional setup.
    augment : bool, optional
        Enable light data augmentation on the training split, by default True.
    normalize : bool, optional
        Apply ImageNet normalization after converting to tensors, by default True.

    Returns
    -------
    dict[str, Any]
        History, metrics, the trained model, and checkpoint path.
    """
    safe_name = name.replace(" ", "-")
    lr_label = _format_lr_label(lr)
    checkpoint_name = f"{safe_name}-b{batch_size}-img{image_size}-e{epochs}-lr-{lr_label}"

    checkpoint_path = MODELS_DIR / "classification" / f"{checkpoint_name}.pt"
    log_path = LOGS_DIR / f"{checkpoint_name}.log"
    results_path = RESULTS_DIR / f"{checkpoint_name}.json"

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    try:
        # ── MLflow: start run and log hyperparameters ─────────────────
        mlflow.set_experiment("echo-brain-tumor")
        mlflow.start_run(run_name=checkpoint_name)
        mlflow.log_params({
            "model": name, "image_size": image_size, "batch_size": batch_size,
            "epochs": epochs, "lr": lr, "augment": augment, "normalize": normalize,
        })

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
        optimizer = AdamW(
            filter(lambda p: p.requires_grad, model.parameters()),
            lr=lr, weight_decay=1e-4,
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs)

        history = {"train_acc": [], "val_acc": []}
        best_state = deepcopy(model.state_dict())
        best_val_acc = 0.0
        best_record = {"epoch": 1, "train_acc": 0.0, "val_acc": 0.0}
        patience = max(10, epochs // 5)
        epochs_no_improve = 0

        for epoch in range(1, epochs + 1):
            _, train_acc = train_one_epoch(model, train_loader, criterion, optimizer)
            scheduler.step()
            _, val_acc = evaluate(model, val_loader, criterion)

            history["train_acc"].append(train_acc)
            history["val_acc"].append(val_acc)

            # ── MLflow: log epoch metrics ────────────────────────────
            mlflow.log_metrics({"train_acc": train_acc, "val_acc": val_acc}, step=epoch)

            progress_message = (
                f"[{name}] epoch {epoch}/{epochs} train_acc={train_acc:.4f} val_acc={val_acc:.4f}"
            )
            _display_progress(progress_message)

            if val_acc > best_val_acc:
                best_val_acc = val_acc
                best_state = deepcopy(model.state_dict())
                best_record = {"epoch": epoch, "train_acc": train_acc, "val_acc": val_acc}
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= patience:
                    _display_progress(f"[{name}] early stopping at epoch {epoch}")
                    break

        model.load_state_dict(best_state)
        torch.save(best_state, checkpoint_path)

        val_loss, val_acc = evaluate(model, val_loader, criterion)
        test_loss, test_acc = evaluate(model, test_loader, criterion)

        # Compute per-class metrics on the test set
        per_class = _per_class_metrics(model, test_loader)

        summary_message = (
            f"[{name}] best={best_record['epoch']}/{epochs} val={best_record['val_acc']:.4f}\n"
            f"[{name}] final val={val_acc:.4f} test={test_acc:.4f}"
            f" macro_f1={per_class['macro_f1']:.4f}\n"
        )

        _display_progress(summary_message)

        experiment_result: dict[str, Any] = {
            "history": history,
            "val_metrics": {"loss": val_loss, "acc": val_acc},
            "test_metrics": {"loss": test_loss, "acc": test_acc},
            "per_class_metrics": per_class,
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

        # Save full results as JSON
        json_ready = {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in experiment_result.items()
            if key != "model"
        }
        with results_path.open("w", encoding="utf-8") as fp:
            json.dump(json_ready, fp, indent=2)

        # Save training curve as interactive HTML plot
        plot_path = RESULTS_DIR / "plots" / f"{checkpoint_name}.html"
        plot_history(
            history,
            f"{name} — Training Curves",
            test_acc=test_acc,
            save_path=plot_path,
        )

        # ── MLflow: log final metrics and artifacts ──────────────────
        mlflow.log_metrics({
            "test_acc": test_acc, "final_val_acc": val_acc,
            "best_epoch": float(best_record["epoch"]),
            "macro_f1": per_class["macro_f1"],
        })
        mlflow.log_artifact(str(checkpoint_path))
        mlflow.log_artifact(str(results_path))
        mlflow.log_artifact(str(plot_path))

        return experiment_result
    finally:
        mlflow.end_run()
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


def _extract_features(
    model: nn.Module,
    loader: DataLoader,
    head_path: tuple[str | int, ...],
) -> tuple[torch.Tensor, torch.Tensor]:
    """Run the frozen backbone and cache its output features.

    Temporarily replaces the classification head with ``Identity`` so the
    model returns raw feature vectors instead of logits.
    """
    # Navigate to the head's parent and swap with Identity
    parent = model
    for segment in head_path[:-1]:
        parent = getattr(parent, segment)
    last = head_path[-1]
    original = parent[last] if isinstance(last, int) else getattr(parent, last)

    identity = nn.Identity()
    if isinstance(last, int):
        parent[last] = identity
    else:
        setattr(parent, last, identity)

    features_list: list[torch.Tensor] = []
    labels_list: list[torch.Tensor] = []
    model.eval()
    with torch.inference_mode():
        for images, labels in loader:
            images = images.to(DEVICE, non_blocking=True)
            with torch.autocast(DEVICE.type, dtype=_AUTOCAST_DTYPE, enabled=_USE_AUTOCAST):
                feats = model(images)
            features_list.append(feats.float().cpu())
            labels_list.append(labels)

    # Restore the original head
    if isinstance(last, int):
        parent[last] = original
    else:
        setattr(parent, last, original)

    return torch.cat(features_list), torch.cat(labels_list)


def tune_hyperparameters(
    name: str,
    train_dir: Path,
    val_dir: Path,
    test_dir: Path,
    image_size: int = 224,
    n_trials: int = 20,
    epochs_per_trial: int = 15,
    augment: bool = True,
    normalize: bool = True,
) -> dict[str, Any]:
    """Run Optuna hyperparameter search for a given model architecture.

    The backbone is frozen, so features are extracted once and cached.
    Only the linear classification head is trained during each trial,
    making the search orders of magnitude faster than a full forward pass
    through the entire network every batch.

    Augmentation is skipped during feature extraction (features are
    deterministic). The full training run after tuning uses augmentation.

    Parameters
    ----------
    name : str
        Model key from MODEL_REGISTRY.
    train_dir : Path
        Training data directory.
    val_dir : Path
        Validation data directory.
    test_dir : Path
        Test data directory.
    image_size : int
        Input resolution.
    n_trials : int
        Number of Optuna trials to run.
    epochs_per_trial : int
        Epochs per trial (shorter than full training for speed).
    augment : bool
        Enable data augmentation (used only in the final training run).
    normalize : bool
        Apply ImageNet normalization.

    Returns
    -------
    dict[str, Any]
        Best trial parameters and the Optuna study object.
    """
    cfg = MODEL_REGISTRY[name]

    # ── Extract backbone features once ────────────────────────────────
    _display_progress(f"[{name}] Extracting backbone features (one-time cost)...")
    model = build_model(name)
    extract_train, extract_val, _ = build_dataloaders(
        train_dir, val_dir, test_dir,
        image_size, batch_size=64,
        augment=False, normalize=normalize,
    )
    train_feats, train_labels = _extract_features(model, extract_train, cfg["head_path"])
    val_feats, val_labels = _extract_features(model, extract_val, cfg["head_path"])
    in_features = train_feats.shape[1]

    _display_progress(
        f"[{name}] Features cached: train={tuple(train_feats.shape)}"
        f" val={tuple(val_feats.shape)}"
    )

    # Free the full model — only the head matters during tuning
    del model
    if DEVICE.type == "mps":
        torch.mps.empty_cache()

    # ── Optuna objective: train only the linear head ──────────────────
    def objective(trial: optuna.Trial) -> float:
        lr = trial.suggest_float("lr", 1e-5, 1e-2, log=True)
        batch_size = trial.suggest_categorical("batch_size", [16, 32, 64])

        train_dl = DataLoader(
            TensorDataset(train_feats, train_labels),
            batch_size=batch_size, shuffle=True,
        )
        val_dl = DataLoader(
            TensorDataset(val_feats, val_labels),
            batch_size=batch_size,
        )

        head = nn.Linear(in_features, NUM_CLASSES).to(DEVICE)
        criterion = nn.CrossEntropyLoss()
        optimizer = AdamW(head.parameters(), lr=lr, weight_decay=1e-4)
        scheduler = CosineAnnealingLR(optimizer, T_max=epochs_per_trial)

        _display_progress(
            f"  Trial {trial.number + 1}/{n_trials} — lr={lr:.2e} batch_size={batch_size}"
        )

        best_val_loss = float("inf")
        for epoch in range(1, epochs_per_trial + 1):
            head.train()
            train_correct = torch.tensor(0, dtype=torch.long, device=DEVICE)
            train_total = 0
            for feats, labels in train_dl:
                feats = feats.to(DEVICE, non_blocking=True)
                labels = labels.to(DEVICE, non_blocking=True)
                optimizer.zero_grad(set_to_none=True)
                out = head(feats)
                loss = criterion(out, labels)
                loss.backward()
                optimizer.step()
                train_correct += (out.detach().argmax(dim=1) == labels).sum()
                train_total += len(labels)
            scheduler.step()
            train_acc = train_correct.item() / train_total

            head.eval()
            val_loss_sum = torch.tensor(0.0, device=DEVICE)
            val_correct = torch.tensor(0, dtype=torch.long, device=DEVICE)
            val_total = 0
            with torch.inference_mode():
                for feats, labels in val_dl:
                    feats = feats.to(DEVICE, non_blocking=True)
                    labels = labels.to(DEVICE, non_blocking=True)
                    out = head(feats)
                    val_loss_sum += criterion(out, labels).detach() * len(labels)
                    val_correct += (out.argmax(dim=1) == labels).sum()
                    val_total += len(labels)
            val_loss = val_loss_sum.item() / val_total
            val_acc = val_correct.item() / val_total

            _display_progress(
                f"    epoch {epoch}/{epochs_per_trial}"
                f"  train_acc={train_acc:.4f}  val_acc={val_acc:.4f}  val_loss={val_loss:.4f}"
            )

            # Abort trials that produce NaN/Inf — the pruner and best-trial
            # selection cannot compare meaningless values.
            if math.isnan(val_loss) or math.isinf(val_loss):
                _display_progress(f"  Trial {trial.number + 1} pruned (NaN/Inf loss) at epoch {epoch}")
                raise optuna.TrialPruned()

            # Report loss (continuous signal) instead of accuracy (saturates at 1.0)
            trial.report(val_loss, epoch)
            if trial.should_prune():
                _display_progress(f"  Trial {trial.number + 1} pruned at epoch {epoch}")
                raise optuna.TrialPruned()

            best_val_loss = min(best_val_loss, val_loss)

        _display_progress(
            f"  Trial {trial.number + 1} done — best_val_loss={best_val_loss:.4f}"
        )
        return best_val_loss

    log_path = LOGS_DIR / f"{name}-tuning.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=42),
        pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=5),
    )
    _display_progress(f"[{name}] Device: {DEVICE} | {epochs_per_trial} epochs/trial | log: {log_path}")
    try:
        study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    finally:
        logger.removeHandler(file_handler)
        file_handler.close()

    best = study.best_trial
    _display_progress(
        f"[{name}] Best trial #{best.number}: val_loss={best.value:.4f} "
        f"lr={best.params['lr']:.2e} batch_size={best.params['batch_size']}"
    )

    return {
        "best_params": best.params,
        "best_value": best.value,
        "study": study,
        "log_path": log_path,
    }


__all__ = [
    "run_experiment",
    "build_model",
    "tune_hyperparameters",
]
