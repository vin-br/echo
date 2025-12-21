"""Plots for training diagnostics and confusion matrices."""

from typing import Dict, Optional

import polars as pl
import plotly.graph_objects as go


def confusion_matrix_count_plot(df: pl.DataFrame, dataset: str, color: str = "Greens") -> None:
    """Confusion-matrix plot with raw counts."""

    index_col, *value_cols = df.columns
    rows = df.get_column(index_col).to_list()
    values = df.select(value_cols).to_numpy()
    fig = go.Figure(
        go.Heatmap(
            z=values, x=value_cols, y=rows, colorscale=color, text=values, texttemplate="%{text}"
        )
    )
    fig.update_layout(
        width=800,
        height=600,
        title=f"Confusion matrix | {dataset} (count)",
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
    )
    fig.show()


def confusion_matrix_distrib_plot(df: pl.DataFrame, dataset: str, color: str = "Greens") -> None:
    """Confusion-matrix plot with column-normalized values."""

    index_col, *value_cols = df.columns
    rows = df.get_column(index_col).to_list()
    values = df.select(value_cols).to_numpy()
    fig = go.Figure(
        go.Heatmap(
            z=values,
            x=value_cols,
            y=rows,
            colorscale=color,
            zmin=0,
            zmax=1,
            text=values,
            texttemplate="%{text:.2%}",
        )
    )
    fig.update_layout(
        width=800,
        height=600,
        title=f"Confusion matrix | {dataset} (distribution)",
        xaxis_title="Predicted Label",
        yaxis_title="True Label",
    )
    fig.show()


def plot_history(history: Dict[str, list], title: str, test_acc: Optional[float] = None) -> None:
    """Plot training/validation accuracy curves plus optional test accuracy."""

    epochs = list(range(1, len(history["train_acc"]) + 1))
    train_trace = go.Scatter(
        x=epochs, y=history["train_acc"], mode="lines+markers", name="Training acc"
    )
    val_trace = go.Scatter(
        x=epochs, y=history["val_acc"], mode="lines+markers", name="Validation acc"
    )
    traces = [train_trace, val_trace]
    if test_acc is not None:
        # Horizontal marker to visualize the held-out test accuracy against epoch curves.
        traces.append(
            go.Scatter(
                x=epochs,
                y=[test_acc] * len(epochs),
                mode="lines",
                name="Test acc",
                line={"dash": "dash"},
            )
        )
    layout = go.Layout(
        width=800, height=600, title=title, xaxis_title="Epochs", yaxis_title="Accuracy"
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.show()


__all__ = [
    "confusion_matrix_count_plot",
    "confusion_matrix_distrib_plot",
    "plot_history",
]
