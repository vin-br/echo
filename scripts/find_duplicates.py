"""Remove duplicate images by hashing file content."""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}


def digest(path: str, chunk: int = 1 << 16) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        while data := handle.read(chunk):
            hasher.update(data)
    return hasher.hexdigest()


def find_duplicates(root: str) -> int:
    seen: dict[str, str] = {}
    removed = 0
    for dirpath, _, files in os.walk(root):
        for name in files:
            if Path(name).suffix.lower() not in IMAGE_EXTS:
                continue
            path = os.path.join(dirpath, name)
            key = digest(path)
            if key in seen:
                print(f"Duplicate detected: {path} matches {seen[key]}")
                os.remove(path)
                removed += 1
            else:
                seen[key] = path
    return removed


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python find_duplicates.py <parent_directory>")
        return 1
    directory = argv[1]
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return 1
    print(f"Removed {find_duplicates(directory)} duplicate files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
