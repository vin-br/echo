"""Dataset enhancement: balance classes, remove low-quality images, augment underrepresented classes.

This script:
1. Identifies and removes near-duplicate images (perceptual hash)
2. Removes low-quality images (too small, low contrast, corrupt)
3. Augments underrepresented classes to match the largest class count
4. Respects the existing naming convention: <PREFIX>_<INDEX>.jpg

Usage:
    python scripts/enhance_dataset.py data/classification/train [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat, UnidentifiedImageError

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
MIN_SIZE = 64           # px — reject images smaller than this
MIN_STD_DEV = 5.0       # pixel value — reject near-uniform images
TARGET_SIZE = (224, 224) # for perceptual hash comparison


def _image_hash(img: Image.Image, size: int = 8) -> str:
    """Compute a difference hash (dHash) for near-duplicate detection."""
    small = img.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(small.get_flattened_data())
    bits = []
    for row in range(size):
        for col in range(size):
            bits.append(pixels[row * (size + 1) + col] > pixels[row * (size + 1) + col + 1])
    return "".join("1" if b else "0" for b in bits)


def _hamming_distance(h1: str, h2: str) -> int:
    return sum(c1 != c2 for c1, c2 in zip(h1, h2))


def _is_low_quality(path: Path) -> str | None:
    """Return a reason string if the image is low quality, else None."""
    try:
        img = Image.open(path)
        img.verify()
        img = Image.open(path)  # reopen after verify
    except (UnidentifiedImageError, OSError, SyntaxError):
        return "corrupt"

    w, h = img.size
    if w < MIN_SIZE or h < MIN_SIZE:
        return f"too_small ({w}x{h})"

    gray = img.convert("L")
    stat = ImageStat.Stat(gray)
    if stat.stddev[0] < MIN_STD_DEV:
        return f"low_contrast (std={stat.stddev[0]:.1f})"

    return None


def _next_index(folder: Path) -> int:
    """Find the next available index for the naming convention."""
    max_idx = -1
    for f in folder.iterdir():
        if not f.is_file():
            continue
        stem = f.stem
        parts = stem.split("_")
        if len(parts) >= 2:
            try:
                idx = int(parts[-1])
                max_idx = max(max_idx, idx)
            except ValueError:
                pass
    return max_idx + 1


def _prefix_for(folder: Path) -> str:
    return folder.name[0].upper()


def _augment_image(img: Image.Image, variant: int) -> Image.Image:
    """Create an augmented variant of the image.

    Each variant applies a different combination of transforms
    to maximize diversity without creating unrealistic images.
    """
    transforms = [
        lambda i: ImageOps.mirror(i),                        # horizontal flip
        lambda i: i.rotate(15, expand=False, fillcolor=0),   # slight rotation
        lambda i: i.rotate(-15, expand=False, fillcolor=0),  # opposite rotation
        lambda i: ImageOps.autocontrast(i, cutoff=2),        # contrast stretch
        lambda i: i.filter(ImageFilter.SHARPEN),             # sharpen
        lambda i: ImageOps.mirror(i.rotate(10, expand=False, fillcolor=0)),  # flip+rotate
        lambda i: ImageOps.equalize(i.convert("RGB")),       # histogram equalize
        lambda i: i.rotate(5, expand=False, fillcolor=0).filter(ImageFilter.SHARPEN),
    ]
    return transforms[variant % len(transforms)](img)


def clean_folder(folder: Path, dry_run: bool = False) -> tuple[int, int]:
    """Remove duplicates and low-quality images. Returns (duplicates, low_quality)."""
    hashes: dict[str, Path] = {}
    dup_count = 0
    lq_count = 0

    files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS)

    for f in files:
        # Check quality first
        reason = _is_low_quality(f)
        if reason:
            print(f"  [low-quality] {f.name}: {reason}")
            if not dry_run:
                f.unlink()
            lq_count += 1
            continue

        # Check for near-duplicates
        try:
            img = Image.open(f).convert("RGB")
        except Exception:
            continue
        h = _image_hash(img)
        duplicate_of = None
        for existing_hash, existing_path in hashes.items():
            if _hamming_distance(h, existing_hash) <= 5:  # threshold: 5 bits out of 64
                duplicate_of = existing_path
                break
        if duplicate_of:
            print(f"  [near-dup] {f.name} ≈ {duplicate_of.name}")
            if not dry_run:
                f.unlink()
            dup_count += 1
        else:
            hashes[h] = f

    return dup_count, lq_count


def augment_folder(folder: Path, target_count: int, dry_run: bool = False) -> int:
    """Augment images in folder to reach target_count. Returns number created."""
    files = sorted(f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS)
    current = len(files)
    needed = target_count - current

    if needed <= 0:
        return 0

    prefix = _prefix_for(folder)
    next_idx = _next_index(folder)
    created = 0

    print(f"  Augmenting {folder.name}: {current} → {target_count} (+{needed})")

    variant = 0
    while created < needed:
        source = files[created % len(files)]
        try:
            img = Image.open(source).convert("RGB")
            aug = _augment_image(img, variant)
            new_name = f"{prefix}_{next_idx:04}.jpg"
            new_path = folder / new_name
            if not dry_run:
                aug.save(new_path, "JPEG", quality=95)
            next_idx += 1
            created += 1
            variant += 1
        except Exception as e:
            print(f"  [warn] Could not augment {source.name}: {e}")
            variant += 1
            if variant > needed * 2:
                break

    return created


def enhance(root: Path, dry_run: bool = False) -> None:
    """Full enhancement pipeline for a classification split directory."""
    if not root.is_dir():
        print(f"Error: {root} is not a directory")
        sys.exit(1)

    class_dirs = sorted(d for d in root.iterdir() if d.is_dir())
    if not class_dirs:
        print(f"No class subdirectories found in {root}")
        sys.exit(1)

    # Phase 1: Clean (remove duplicates + low-quality)
    print("\n=== Phase 1: Cleaning ===")
    total_dups = 0
    total_lq = 0
    for cls_dir in class_dirs:
        print(f"\nCleaning {cls_dir.name}/")
        dups, lq = clean_folder(cls_dir, dry_run=dry_run)
        total_dups += dups
        total_lq += lq
    print(f"\nCleaning summary: {total_dups} near-duplicates, {total_lq} low-quality removed")

    # Phase 2: Count after cleaning
    counts = {}
    for cls_dir in class_dirs:
        files = [f for f in cls_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
        counts[cls_dir.name] = len(files)

    print("\n=== Post-cleaning distribution ===")
    for name, count in sorted(counts.items()):
        print(f"  {name}: {count}")

    max_count = max(counts.values())

    # Phase 3: Augment underrepresented classes
    print(f"\n=== Phase 2: Augmenting to {max_count} per class ===")
    total_aug = 0
    for cls_dir in class_dirs:
        created = augment_folder(cls_dir, max_count, dry_run=dry_run)
        total_aug += created

    # Final summary
    print("\n=== Final distribution ===")
    for cls_dir in class_dirs:
        files = [f for f in cls_dir.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS]
        count = len(files) if not dry_run else counts[cls_dir.name]
        print(f"  {cls_dir.name}: {count}")
    print(f"\nTotal augmented images created: {total_aug}")

    if dry_run:
        print("\n[DRY RUN] No files were modified.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Enhance classification dataset")
    parser.add_argument("directory", type=Path, help="Path to the split directory (e.g., data/classification/train)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without modifying files")
    args = parser.parse_args()
    enhance(args.directory.resolve(), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
