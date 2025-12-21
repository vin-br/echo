"""Split each tumor class folder into training/testing folders."""

from __future__ import annotations

import random
import shutil
from pathlib import Path

LABELS = ("glioma_tumor", "meningioma_tumor", "no_tumor", "pituitary_tumor")
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def sample_folder(root: Path, label: str, rate: float) -> None:
    src = root / label
    if not src.is_dir():
        return
    files = [p for p in src.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    if not files:
        return
    count = max(1, int(len(files) * rate))
    dest = root / "testing" / label
    dest.mkdir(parents=True, exist_ok=True)
    for path in random.sample(files, min(count, len(files))):
        shutil.move(path, dest / path.name)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python split_dataset.py <parent_folder> [selection_rate]")
        return 1
    root = Path(argv[1]).expanduser().resolve()
    if not root.is_dir():
        print(f"Folder not found: {root}")
        return 1
    rate = float(argv[2]) if len(argv) > 2 else 0.20
    (root / "testing").mkdir(exist_ok=True)
    for label in LABELS:
        sample_folder(root, label, rate)
    print("Testing split created.")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
