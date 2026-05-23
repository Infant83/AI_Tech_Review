#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_RETENTION_DAYS = 7
DEFAULT_TEMP_SUBDIR = ("AI_Tech_Review", "skywork")
DEFAULT_GLOB = "skywork*.png"


@dataclass(frozen=True)
class Config:
    temp_dir: Path
    retention_days: int


def resolve_config(retention_days: int | None) -> Config:
    env_dir = os.environ.get("AI_TECH_REVIEW_SKYWORK_TEMP_DIR")
    if env_dir:
        temp_dir = Path(env_dir).expanduser().resolve()
    else:
        temp_dir = Path(tempfile.gettempdir(), *DEFAULT_TEMP_SUBDIR).resolve()

    env_retention = os.environ.get("AI_TECH_REVIEW_SKYWORK_TEMP_RETENTION_DAYS")
    if retention_days is None:
        retention_days = int(env_retention) if env_retention else DEFAULT_RETENTION_DAYS

    return Config(temp_dir=temp_dir, retention_days=max(1, retention_days))


def ensure_temp_dir(config: Config) -> Path:
    config.temp_dir.mkdir(parents=True, exist_ok=True)
    return config.temp_dir


def cleanup_old_files(config: Config) -> tuple[list[Path], list[Path]]:
    ensure_temp_dir(config)
    cutoff = datetime.now() - timedelta(days=config.retention_days)
    removed: list[Path] = []

    for entry in config.temp_dir.iterdir():
        if not entry.is_file():
            continue
        if datetime.fromtimestamp(entry.stat().st_mtime) < cutoff:
            entry.unlink(missing_ok=True)
            removed.append(entry)

    removed_dirs: list[Path] = []
    for entry in sorted(config.temp_dir.iterdir(), reverse=True):
        if entry.is_dir() and not any(entry.iterdir()):
            entry.rmdir()
            removed_dirs.append(entry)

    return removed, removed_dirs


def unique_target_path(base_dir: Path, file_name: str) -> Path:
    stem = Path(file_name).stem
    suffix = Path(file_name).suffix or ".png"
    candidate = base_dir / f"{stem}{suffix}"
    index = 2
    while candidate.exists():
        candidate = base_dir / f"{stem}_{index}{suffix}"
        index += 1
    return candidate


def allocate_temp_path(config: Config, file_name: str | None) -> Path:
    cleanup_old_files(config)
    ensure_temp_dir(config)
    if not file_name:
        file_name = f"skywork_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    file_name = Path(file_name).name
    return unique_target_path(config.temp_dir, file_name)


def migrate_workspace_files(config: Config, workspace_root: Path, pattern: str) -> list[tuple[Path, Path]]:
    cleanup_old_files(config)
    ensure_temp_dir(config)

    moved: list[tuple[Path, Path]] = []
    for source in sorted(workspace_root.glob(pattern)):
        if not source.is_file():
            continue
        target = unique_target_path(config.temp_dir, source.name)
        shutil.move(str(source), str(target))
        moved.append((source, target))
    return moved


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manage temporary Skywork screenshot files outside the workspace.",
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=None,
        help=f"Delete temp files older than this many days (default: {DEFAULT_RETENTION_DAYS}).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("dir", help="Print the active Skywork temp directory after cleanup.")

    alloc_parser = subparsers.add_parser("alloc", help="Allocate a temp screenshot path and print it.")
    alloc_parser.add_argument("--name", help="Preferred file name, e.g. skywork_status.png")

    cleanup_parser = subparsers.add_parser("cleanup", help="Delete expired temp files and print what was removed.")
    cleanup_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print removed files line by line.",
    )

    migrate_parser = subparsers.add_parser(
        "migrate-workspace",
        help="Move workspace-root skywork*.png files into the temp directory.",
    )
    migrate_parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root to scan (default: current directory).",
    )
    migrate_parser.add_argument(
        "--pattern",
        default=DEFAULT_GLOB,
        help=f"Glob pattern to move (default: {DEFAULT_GLOB}).",
    )

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = resolve_config(args.retention_days)

    if args.command == "dir":
        cleanup_old_files(config)
        print(ensure_temp_dir(config))
        return 0

    if args.command == "alloc":
        print(allocate_temp_path(config, args.name))
        return 0

    if args.command == "cleanup":
        removed_files, removed_dirs = cleanup_old_files(config)
        if args.verbose:
            for removed in removed_files + removed_dirs:
                print(removed)
        else:
            print(
                f"removed_files={len(removed_files)} removed_dirs={len(removed_dirs)} temp_dir={config.temp_dir}",
            )
        return 0

    if args.command == "migrate-workspace":
        workspace_root = Path(args.workspace_root).resolve()
        moved = migrate_workspace_files(config, workspace_root, args.pattern)
        for source, target in moved:
            print(f"{source} -> {target}")
        if not moved:
            print(f"no_matches pattern={args.pattern} workspace_root={workspace_root}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
