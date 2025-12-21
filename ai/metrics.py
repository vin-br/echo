"""Metrics for model evaluation."""

import json
import logging
import polars as pl
import torch

from pathlib import Path
from typing import Any, Dict, Iterable, List

from shared.paths import RESULTS_DIR

logger = logging.getLogger(__name__)


def _unique_labels(*columns: Iterable[str]) -> List[str]:
    seen: dict[str, None] = {}
    for column in columns:
        for value in column:
            if value not in seen:
                seen[value] = None
    return list(seen.keys())


def load_results(json_path: Path | str):
    """Load results saved as JSON from ``RESULTS_DIR``.

    Accepts either a filename (relative to RESULTS_DIR) or an absolute path.
    """

    json_path = Path(json_path)
    if not json_path.is_absolute():
        json_path = RESULTS_DIR / json_path

    with json_path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    data["checkpoint_path"] = Path(data["checkpoint_path"])
    data["log_path"] = Path(data["log_path"])
    data["results_path"] = Path(data["results_path"])
    return data


def confusion_matrix_count(
    df: pl.DataFrame,
    predicted_col: str = "Predicted Label",
    true_col: str = "True Label",
) -> pl.DataFrame:
    """Compute confusion-matrix counts using Torch for concise logic."""

    if df.height == 0:
        return pl.DataFrame({predicted_col: [], true_col: []})

    preds = df.get_column(predicted_col).to_list()
    trues = df.get_column(true_col).to_list()
    labels = _unique_labels(preds, trues)

    index_map = {label: idx for idx, label in enumerate(labels)}
    pred_idx = torch.tensor([index_map[label] for label in preds], dtype=torch.long)
    true_idx = torch.tensor([index_map[label] for label in trues], dtype=torch.long)

    num_classes = len(labels)
    flat_indices = pred_idx * num_classes + true_idx
    counts = torch.bincount(flat_indices, minlength=num_classes * num_classes)
    counts = counts.view(num_classes, num_classes)

    data = {predicted_col: labels}
    for col_idx, label in enumerate(labels):
        data[label] = counts[:, col_idx].tolist()
    return pl.DataFrame(data)


def confusion_matrix_distrib(df: pl.DataFrame) -> pl.DataFrame:
    """Normalize ``confusion_matrix_count`` output column-wise using Torch."""

    if df.height == 0 or len(df.columns) <= 1:
        return df

    label_col, *value_cols = df.columns
    counts = torch.tensor(df.select(value_cols).to_numpy(), dtype=torch.float32)
    column_totals = counts.sum(dim=0, keepdim=True).clamp_min(1.0)
    distrib = counts / column_totals

    data = {label_col: df.get_column(label_col).to_list()}
    for idx, col in enumerate(value_cols):
        data[col] = distrib[:, idx].tolist()
    return pl.DataFrame(data)


def display_results(label: str, results: Dict[str, Any]) -> None:
    """Structured summary of a ``run_experiment`` result dictionary."""

    cfg = results.get("config", {})
    best_epoch = results.get("best_epoch", float("nan"))
    best_metrics = results.get("best_epoch_metrics", {})
    params_summary = (
        "image_size={image_size}, batch_size={batch_size}, lr={lr}, augment={augment}, "
        "normalize={normalize}"
    ).format(
        image_size=cfg.get("image_size", "?"),
        batch_size=cfg.get("batch_size", "?"),
        lr=cfg.get("lr", "?"),
        augment=cfg.get("augment", "?"),
        normalize=cfg.get("normalize", "?"),
    )

    message = (
        f"{label} - Best epoch: {best_epoch}/{cfg.get('epochs', 0)} "
        f"(validation: {best_metrics.get('val_acc', float('nan')):.4f})\n"
        f"Final validation: {results['val_metrics']['acc']:.4f} "
        f"| Test: {results['test_metrics']['acc']:.4f}\n"
        f"Parameters: {params_summary}\n"
        f"Checkpoint: {results['checkpoint_path']}"
    )

    logger.info(message)
    print(message)


__all__ = [
    "load_results",
    "confusion_matrix_count",
    "confusion_matrix_distrib",
    "display_results",
]
