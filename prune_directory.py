#!/usr/bin/env python3
"""Prune a directory while preserving large videos and image files.

The script traverses the given source directory and performs the following actions:

* Video files (based on the extension list) that are **at least 200 MB** in size
  are *kept* by moving them into the target directory, preserving the relative
  structure from the source.
* Image files (based on the extension list) are kept in the same manner.
* All other file types are deleted from the source directory.
* Directories that do not contain any kept video files (200 MB or larger) are
  removed from the source after their contents are processed. Empty directories
  left behind after moving files are also cleaned up.

Usage:
    python prune_directory.py <source_directory> <target_directory>
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MIN_VIDEO_SIZE_BYTES = 200 * 1024 * 1024

VIDEO_EXTENSIONS = {
    ".3gp",
    ".avi",
    ".flv",
    ".m2ts",
    ".m4v",
    ".mkv",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mts",
    ".ts",
    ".wmv",
}

IMAGE_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".heic",
    ".heif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


@dataclass
class Stats:
    """Collection of counters recorded during the pruning run."""

    videos_kept: int = 0
    videos_deleted: int = 0
    images_kept: int = 0
    other_deleted: int = 0
    dirs_removed: int = 0
    collisions_resolved: int = 0


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prune a directory tree")
    parser.add_argument("source", type=Path, help="Source directory to prune")
    parser.add_argument(
        "target",
        type=Path,
        help=(
            "Directory where kept files will be moved, preserving the relative "
            "structure"
        ),
    )
    return parser.parse_args(argv)


def ensure_valid_directories(source: Path, target: Path) -> None:
    if not source.exists():
        raise SystemExit(f"Source directory '{source}' does not exist")

    if not source.is_dir():
        raise SystemExit(f"Source path '{source}' is not a directory")

    if target.exists() and not target.is_dir():
        raise SystemExit(f"Target path '{target}' exists and is not a directory")

    if source.resolve() == target.resolve():
        raise SystemExit("Source and target directories must be different")

    try:
        if target.resolve().is_relative_to(source.resolve()):
            raise SystemExit("Target directory must not be inside the source directory")
    except AttributeError:
        # For Python versions < 3.9 where Path.is_relative_to is unavailable
        try:
            target.resolve().relative_to(source.resolve())
        except ValueError:
            pass
        else:
            raise SystemExit(
                "Target directory must not be inside the source directory"
            )

    target.mkdir(parents=True, exist_ok=True)


def resolve_collision(dest_path: Path) -> Path:
    suffixes = "".join(dest_path.suffixes)
    base_name = dest_path.name[: -len(suffixes)] if suffixes else dest_path.name
    if not base_name:
        base_name = dest_path.stem or dest_path.name

    parent = dest_path.parent
    counter = 1
    while True:
        candidate = parent / f"{base_name}_{counter}{suffixes}"
        if not candidate.exists():
            return candidate
        counter += 1


def move_to_target(file_path: Path, source_root: Path, target_root: Path, stats: Stats) -> None:
    relative_path = file_path.relative_to(source_root)
    destination = target_root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)

    final_destination = destination
    if destination.exists():
        final_destination = resolve_collision(destination)
        final_destination.parent.mkdir(parents=True, exist_ok=True)
        stats.collisions_resolved += 1

    shutil.move(str(file_path), str(final_destination))


def safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except PermissionError as exc:
        raise SystemExit(f"Failed to delete '{path}': {exc}") from exc


def remove_directory(path: Path, stats: Stats) -> None:
    if not path.exists():
        return
    shutil.rmtree(path)
    stats.dirs_removed += 1


def is_video_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in VIDEO_EXTENSIONS


def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def handle_file(
    file_path: Path,
    source_root: Path,
    target_root: Path,
    stats: Stats,
) -> bool:
    """Process a single file. Returns True when a video >= 200 MB was kept."""

    if is_video_file(file_path):
        try:
            size = file_path.stat().st_size
        except OSError as exc:
            raise SystemExit(f"Unable to read size for '{file_path}': {exc}") from exc

        if size >= MIN_VIDEO_SIZE_BYTES:
            move_to_target(file_path, source_root, target_root, stats)
            stats.videos_kept += 1
            return True

        safe_unlink(file_path)
        stats.videos_deleted += 1
        return False

    if is_image_file(file_path):
        move_to_target(file_path, source_root, target_root, stats)
        stats.images_kept += 1
        return False

    safe_unlink(file_path)
    stats.other_deleted += 1
    return False


def is_directory_empty(directory: Path) -> bool:
    try:
        next(directory.iterdir())
    except StopIteration:
        return True
    return False


def process_directory(
    directory: Path,
    source_root: Path,
    target_root: Path,
    stats: Stats,
) -> bool:
    """Traverse *directory* and prune its contents.

    Returns True if this subtree contained at least one kept (>=200 MB) video file.
    """

    kept_video_found = False

    try:
        entries = sorted(directory.iterdir(), key=lambda p: p.name.lower())
    except PermissionError as exc:
        raise SystemExit(f"Cannot access directory '{directory}': {exc}") from exc

    for entry in entries:
        if entry.is_symlink():
            safe_unlink(entry)
            stats.other_deleted += 1
            continue

        if entry.is_file():
            if handle_file(entry, source_root, target_root, stats):
                kept_video_found = True
            continue

        if entry.is_dir():
            child_has_video = process_directory(entry, source_root, target_root, stats)
            if child_has_video:
                kept_video_found = True
                if is_directory_empty(entry):
                    remove_directory(entry, stats)
            else:
                remove_directory(entry, stats)

    return kept_video_found


def main(argv: Iterable[str]) -> None:
    args = parse_args(argv)
    source_root = args.source.resolve()
    target_root = args.target.resolve()

    ensure_valid_directories(source_root, target_root)

    stats = Stats()
    kept_video_in_root = process_directory(source_root, source_root, target_root, stats)

    print("Pruning completed.")
    print(f"Kept videos (moved): {stats.videos_kept}")
    print(f"Deleted videos (<200MB): {stats.videos_deleted}")
    print(f"Kept images (moved): {stats.images_kept}")
    print(f"Deleted other files: {stats.other_deleted}")
    print(f"Directories removed: {stats.dirs_removed}")
    if stats.collisions_resolved:
        print(f"Name collisions resolved: {stats.collisions_resolved}")
    if not kept_video_in_root:
        print("No video files over 200MB were found in the source directory.")


if __name__ == "__main__":
    main(sys.argv[1:])
