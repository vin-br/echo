"""Rename every file within a folder using a simple prefix + counter."""

from __future__ import annotations

import sys
from pathlib import Path


def rename_files_in_folder(folder: Path) -> None:
    """Rename all files in *folder* using `<prefix>_<index>.<ext>`."""

    if not folder.is_dir():
        raise ValueError(f"Folder not found: {folder}")
    prefix = folder.name[:1].upper()
    files = sorted(p for p in folder.iterdir() if p.is_file())
    for idx, path in enumerate(files):
        suffix = path.suffix
        new_name = f"{prefix}_{idx:04}{suffix}"
        new_path = path.with_name(new_name)
        path.rename(new_path)
    print(f"Renamed {len(files)} files in {folder}.")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python rename_files.py <folder>")
        return 1
    folder = Path(argv[1]).expanduser().resolve()
    try:
        rename_files_in_folder(folder)
    except ValueError as exc:
        print(exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
