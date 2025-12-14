"""CLI entry point for launching Arc training runs."""

import argparse
import io
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any, TextIO, cast

import polars as pl
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.prompt import Prompt

from ai.config import MODEL_REGISTRY
from ai.trainer import build_model, run_experiment
from modules.paths import TESTING_DATASET, TRAINING_DATASET, RESULTS_DIR

EPOCH_PATTERN = re.compile(r"Epoch\s+(?P<current>\d+)/(?:\s*)(?P<total>\d+)")
COMMON_LRS = (1e-3, 5e-4, 1e-4)
EXIT_WORDS = {"exit", "quit", "q", "leave", "stop", "bye"}


class ProgressLogger(io.TextIOBase):
    """Intercept stdout/stderr to update Rich progress and persist logs."""

    def __init__(self, console: Console, progress: Progress, task_id: TaskID) -> None:
        super().__init__()
        self.console = console
        self.progress = progress
        self.task_id = task_id
        self.buffer = ""

    def write(self, data: str) -> int:  # type: ignore[override]
        self.buffer += data
        while "\n" in self.buffer:
            line, self.buffer = self.buffer.split("\n", 1)
            if not line:
                continue
            self.console.print(line)
            match = EPOCH_PATTERN.search(line)
            if match:
                current = int(match.group("current"))
                self.progress.update(self.task_id, completed=current)
        return len(data)

    def flush(self) -> None:  # pragma: no cover - TextIOBase compatibility
        return


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Arc models via CLI")
    parser.add_argument("model", nargs="?", choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--augment", dest="augment", action="store_true", default=True)
    parser.add_argument("--no-augment", dest="augment", action="store_false")
    parser.add_argument("--normalize", dest="normalize", action="store_true", default=True)
    parser.add_argument("--no-normalize", dest="normalize", action="store_false")
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Show the available model keys and exit",
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Prompt for configuration values instead of passing every flag",
    )
    return parser.parse_args()


def render_model_list() -> str:
    lines = ["Available models:"]
    for key in sorted(MODEL_REGISTRY.keys()):
        lines.append(f"  - {key}")
    return "\n".join(lines)


def format_common_lrs() -> str:
    return ", ".join(f"{lr:g}" for lr in COMMON_LRS)


def save_history(artifact_name: str, results: dict[str, Any], results_dir: Path) -> Path:
    history = results["history"]
    epochs = list(range(1, len(history["train_acc"]) + 1))
    df = pl.DataFrame(
        {
            "run": artifact_name,
            "epoch": epochs,
            "train_acc": history["train_acc"],
            "val_acc": history["val_acc"],
            "val_best": float(results["val_metrics"]["acc"]),
            "test_acc": float(results["test_metrics"]["acc"]),
        }
    )
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{artifact_name}-history.parquet"
    df.write_parquet(path)
    return path


def interactive_fill(args: argparse.Namespace, console: Console) -> None:
    console.print(render_model_list())
    console.print(f"Common learning rates: {format_common_lrs()}\n")

    prompt_items = [
        ("model", "Select model", args.model or ""),
        ("image_size", "Image size", str(args.image_size)),
        ("batch_size", "Batch size", str(args.batch_size)),
        ("epochs", "Epochs", str(args.epochs)),
        (
            "lr",
            f"Learning rate ({format_common_lrs()})",
            str(args.lr),
        ),
        ("augment", "Enable augmentation? (y/n)", "y" if args.augment else "n"),
        ("normalize", "Normalize inputs? (y/n)", "y" if args.normalize else "n"),
    ]

    for key, message, default in prompt_items:
        while True:
            value = Prompt.ask(message, default=default if default != "" else None)
            if value is None:
                value = ""
            if value.strip().lower() in EXIT_WORDS:
                raise SystemExit("Exiting training CLI as requested.")

            match key:
                case "model":
                    if value in MODEL_REGISTRY:
                        args.model = value
                        break
                    console.print(f"[red]Invalid model:[/red] {value}")
                case "image_size" | "batch_size" | "epochs":
                    try:
                        setattr(args, key, int(value))
                        break
                    except ValueError:
                        console.print("[red]Enter a valid integer.[/red]")
                case "lr":
                    try:
                        args.lr = float(value)
                        break
                    except ValueError:
                        console.print("[red]Enter a valid number.[/red]")
                case "augment" | "normalize":
                    normalized = value.strip().lower()
                    if normalized in {"y", "yes"}:
                        setattr(args, key, True)
                        break
                    if normalized in {"n", "no"}:
                        setattr(args, key, False)
                        break
                    console.print("[red]Please answer with 'y' or 'n'.[/red]")

    console.print("")


def main() -> None:
    args = parse_args()
    console = Console(file=sys.__stdout__, record=True)
    console.print("[bold green]Welcome to the Arc Training CLI[/bold green]\n")
    if args.list_models:
        console.print(render_model_list())
        console.print(f"Common learning rates: {format_common_lrs()}")
        return
    if args.interactive:
        interactive_fill(args, console)
    if args.model is None:
        raise SystemExit("Model selection is required (pass a value or use --interactive).")
    console.rule(f"[bold cyan]Training {args.model}")

    results_dir: Path = RESULTS_DIR
    required_dirs = {
        "TRAINING_DATASET": TRAINING_DATASET,
        "VALIDATION_DATASET": TESTING_DATASET,
        "TESTING_DATASET": TESTING_DATASET,
    }
    missing = [name for name, path in required_dirs.items() if not path.is_dir()]
    if missing:
        detail = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing required dataset directories (configure via modules.paths): {detail}"
        )

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
        console=console,
    ) as progress:
        descriptor = f"{args.model} img{args.image_size} bs{args.batch_size}"
        task_id = progress.add_task(f"Training {descriptor}", total=args.epochs)
        writer = ProgressLogger(console, progress, task_id)
        text_writer = cast(TextIO, writer)
        with redirect_stdout(text_writer), redirect_stderr(text_writer):
            results = run_experiment(
                name=args.model,
                model_builder=lambda: build_model(args.model),
                train_dir=TRAINING_DATASET,
                val_dir=TESTING_DATASET,
                test_dir=TESTING_DATASET,
                image_size=args.image_size,
                batch_size=args.batch_size,
                epochs=args.epochs,
                lr=args.lr,
                augment=args.augment,
                normalize=args.normalize,
            )

    artifact_name = Path(results["checkpoint_path"]).stem
    history_path = save_history(artifact_name, results, results_dir)

    console.rule("[green]Run complete")
    console.print(
        f"History saved to [bold]{history_path}[/bold]\n"
        f"Checkpoint saved to [bold]{results['checkpoint_path']}[/bold]\n"
        f"Metrics JSON saved to [bold]{results['results_path']}[/bold]\n"
        f"Logs saved to [bold]{results['log_path']}[/bold]",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[red]Training interrupted by user.[/red]")
