"""Plots for training diagnostics."""

from pathlib import Path

import plotly.graph_objects as go


def plot_history(
    history: dict[str, list],
    title: str,
    test_acc: float | None = None,
    save_path: Path | None = None,
) -> go.Figure:
    """Plot training/validation accuracy curves plus optional test accuracy.

    Returns the Plotly Figure. When *save_path* is provided the chart is also
    written as a self-contained HTML file (Plotly.js loaded from CDN).
    """

    epochs = list(range(1, len(history["train_acc"]) + 1))
    train_trace = go.Scatter(
        x=epochs, y=history["train_acc"], mode="lines+markers", name="Training acc"
    )
    val_trace = go.Scatter(
        x=epochs, y=history["val_acc"], mode="lines+markers", name="Validation acc"
    )
    traces = [train_trace, val_trace]
    if test_acc is not None:
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
        autosize=True,
        xaxis_title="Epochs",
        yaxis_title="Accuracy",
        margin={"l": 50, "r": 20, "t": 20, "b": 50},
    )
    fig = go.Figure(data=traces, layout=layout)

    if save_path is not None:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        # Inject CSS so the chart fills the iframe viewport exactly
        _fill_viewport_css = (
            "var s=document.createElement('style');"
            "s.textContent='html,body{margin:0;padding:0;height:100%;overflow:hidden;background:transparent}"
            " .plotly-graph-div{width:100%!important;height:100vh!important}';"
            "document.head.appendChild(s);"
            "window.dispatchEvent(new Event('resize'));"
        )
        fig.write_html(
            str(save_path),
            include_plotlyjs="cdn",
            config={"responsive": True},
            post_script=_fill_viewport_css,
        )

    return fig


__all__ = [
    "plot_history",
]
