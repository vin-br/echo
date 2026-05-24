"""CLI for YOLOv8 brain tumor detection training."""

import argparse
import sys
from pathlib import Path

from rich.console import Console

from vision.detection.engine import DEFAULTS, train
from vision.common.paths import DETECTION_DATASET, MODELS_DIR

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 on brain tumor detection dataset",
    )
    parser.add_argument("--model", default=DEFAULTS["model"], help="YOLO base model (default: yolov8n.pt)")
    parser.add_argument("--epochs", type=int, default=DEFAULTS["epochs"], help="Max epochs")
    parser.add_argument("--batch", type=int, default=DEFAULTS["batch"], help="Batch size")
    parser.add_argument("--imgsz", type=int, default=DEFAULTS["imgsz"], help="Image size")
    parser.add_argument("--lr0", type=float, default=DEFAULTS["lr0"], help="Initial learning rate")
    parser.add_argument("--patience", type=int, default=DEFAULTS["patience"], help="Early stopping patience")
    parser.add_argument("--device", default=DEFAULTS["device"], help="Device (cpu, 0, mps)")
    parser.add_argument("--data", type=Path, default=None, help="Path to data.yaml")
    args = parser.parse_args()

    data_yaml = args.data or DETECTION_DATASET / "data.yaml"
    if not data_yaml.exists():
        console.print(f"[red]Dataset config not found:[/red] {data_yaml}")
        console.print("Download a YOLOv8 brain tumor dataset and place it in data/detection/")
        sys.exit(1)

    console.print("\n[bold]YOLOv8 Detection Training[/bold]")
    console.print(f"  Model    : {args.model}")
    console.print(f"  Epochs   : {args.epochs}")
    console.print(f"  Batch    : {args.batch}")
    console.print(f"  Image    : {args.imgsz}px")
    console.print(f"  LR       : {args.lr0}")
    console.print(f"  Patience : {args.patience}")
    console.print(f"  Device   : {args.device}")
    console.print(f"  Dataset  : {data_yaml}\n")

    try:
        best = train(
            model=args.model,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            lr0=args.lr0,
            patience=args.patience,
            device=args.device,
            data_yaml=data_yaml,
        )
        console.print(f"\n[green]Training complete.[/green] Best weights: {best}")
        console.print(f"Model copied to: {MODELS_DIR / 'detection' / 'yolo-brain-tumor.pt'}")
    except Exception as exc:
        console.print(f"\n[red]Training failed:[/red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
