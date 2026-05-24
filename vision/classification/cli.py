"""CLI entry point for launching ECHO training runs."""

import argparse
import io
import re
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import TextIO, cast

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

from vision.common.config import MODEL_REGISTRY
from vision.classification.engine import build_model, run_experiment, tune_hyperparameters
from vision.common.paths import TESTING_DATASET, TRAINING_DATASET

EPOCH_PATTERN = re.compile(r"Epoch\s+(?P<current>\d+)/(?:\s*)(?P<total>\d+)")
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
    parser = argparse.ArgumentParser(description="Train ECHO models via CLI")
    parser.add_argument("model", nargs="?", choices=sorted(MODEL_REGISTRY.keys()))
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Batch size (omit to let Optuna find optimal value)")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=None,
                        help="Learning rate (omit to let Optuna find optimal value)")
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
    parser.add_argument(
        "--n-trials",
        type=int,
        default=20,
        help="Number of Optuna trials for hyperparameter search (default: 20)",
    )
    return parser.parse_args()


def render_model_list() -> str:
    lines = ["Available models:"]
    for key in sorted(MODEL_REGISTRY.keys()):
        lines.append(f"  - {key}")
    return "\n".join(lines)


def interactive_fill(args: argparse.Namespace, console: Console) -> None:
    console.print(render_model_list())
    console.print()

    prompt_items = [
        ("model", "Select model", args.model or ""),
        ("image_size", "Image size", str(args.image_size)),
        ("epochs", "Epochs", str(args.epochs)),
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
                case "image_size" | "epochs":
                    try:
                        setattr(args, key, int(value))
                        break
                    except ValueError:
                        console.print("[red]Enter a valid integer.[/red]")
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
    console.print("[bold green]Welcome to the ECHO Training CLI[/bold green]\n")
    if args.list_models:
        console.print(render_model_list())
        return
    if args.interactive:
        interactive_fill(args, console)
    if args.model is None:
        raise SystemExit("Model selection is required (pass a value or use --interactive).")

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

    # Optuna hyperparameter search (default pipeline)
    needs_tuning = args.lr is None or args.batch_size is None
    if needs_tuning:
        console.rule(f"[bold magenta]Tuning {args.model} ({args.n_trials} trials)")
        tune_result = tune_hyperparameters(
            name=args.model,
            train_dir=TRAINING_DATASET,
            val_dir=TESTING_DATASET,
            test_dir=TESTING_DATASET,
            image_size=args.image_size,
            n_trials=args.n_trials,
            augment=args.augment,
            normalize=args.normalize,
        )
        best = tune_result["best_params"]
        console.print("\n[bold green]Best hyperparameters:[/bold green]")
        for k, v in best.items():
            console.print(f"  {k}: {v}")
        console.print(f"  val_loss: {tune_result['best_value']:.4f}\n")

        # Apply found params (user overrides take precedence)
        if args.lr is None:
            args.lr = best["lr"]
        if args.batch_size is None:
            args.batch_size = best["batch_size"]
    else:
        console.print("[dim]Using provided hyperparameters (skipping Optuna search).[/dim]\n")

    console.rule(f"[bold cyan]Training {args.model}")

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

    console.rule("[green]Run complete")
    console.print(
        f"Checkpoint saved to [bold]{results['checkpoint_path']}[/bold]\n"
        f"Metrics JSON saved to [bold]{results['results_path']}[/bold]\n"
        f"Logs saved to [bold]{results['log_path']}[/bold]\n"
        f"MLflow run: [bold]{artifact_name}[/bold]",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        Console().print("\n[red]Training interrupted by user.[/red]")
