"""Generate dataset distribution plot for README documentation."""

from pathlib import Path

import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "classification"
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"

CLASSES = ["glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor"]
LABELS = ["Glioma Tumor", "Meningioma Tumor", "No Tumor", "Pituitary Tumor"]


def count_images(split: str) -> list[int]:
    return [len(list((DATA_DIR / split / cls).glob("*"))) for cls in CLASSES]


def main() -> None:
    train_counts = count_images("train")
    test_counts = count_images("test")
    total_train = sum(train_counts)
    total_test = sum(test_counts)

    # Print stratification table
    print("=== Dataset Distribution ===")
    print(f"{'Class':<20} {'Train':>6} {'%':>7}  {'Test':>6} {'%':>7}  {'Δ%':>6}")
    print("-" * 60)
    for i, cls in enumerate(CLASSES):
        train_pct = train_counts[i] / total_train * 100
        test_pct = test_counts[i] / total_test * 100
        delta = abs(train_pct - test_pct)
        print(
            f"{cls:<20} {train_counts[i]:>6} {train_pct:>6.1f}%"
            f"  {test_counts[i]:>6} {test_pct:>6.1f}%  {delta:>5.2f}%"
        )
    print("-" * 60)
    print(f"{'Total':<20} {total_train:>6}          {total_test:>6}")
    ratio = total_train / (total_train + total_test) * 100
    print(f"\nTrain/Test split: {total_train}/{total_test} ({ratio:.0f}/{100 - ratio:.0f})")

    train_pcts = [c / total_train * 100 for c in train_counts]
    test_pcts = [c / total_test * 100 for c in test_counts]

    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.6, 0.4],
        subplot_titles=["Class Distribution (counts)", "Stratification Check (%)"],
        horizontal_spacing=0.12,
    )

    # Left: grouped bar chart (counts)
    fig.add_trace(
        go.Bar(
            x=LABELS,
            y=train_counts,
            name=f"Train (n={total_train})",
            marker_color="#4a90d9",
            text=train_counts,
            textposition="outside",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Bar(
            x=LABELS,
            y=test_counts,
            name=f"Test (n={total_test})",
            marker_color="#d94a4a",
            text=test_counts,
            textposition="outside",
        ),
        row=1,
        col=1,
    )

    # Right: proportion comparison (train vs test %)
    fig.add_trace(
        go.Bar(
            y=LABELS,
            x=train_pcts,
            name="Train %",
            marker_color="#4a90d9",
            text=[f"{p:.1f}%" for p in train_pcts],
            textposition="outside",
            orientation="h",
            showlegend=False,
        ),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Bar(
            y=LABELS,
            x=test_pcts,
            name="Test %",
            marker_color="#d94a4a",
            text=[f"{p:.1f}%" for p in test_pcts],
            textposition="outside",
            orientation="h",
            showlegend=False,
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        barmode="group",
        plot_bgcolor="#fafafa",
        paper_bgcolor="#fafafa",
        width=1200,
        height=450,
        margin=dict(t=50, b=40, l=60, r=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="left", x=0),
        font=dict(size=12),
    )
    fig.update_yaxes(title_text="Number of images", row=1, col=1)
    fig.update_xaxes(title_text="Proportion (%)", range=[0, 40], row=1, col=2)

    output = MEDIA_DIR / "data-distribution.png"
    fig.write_image(str(output), scale=2)
    print(f"\nPlot saved to {output}")


if __name__ == "__main__":
    main()
