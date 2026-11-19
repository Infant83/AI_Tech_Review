"""Create an isolated local read-only inventory; never build or publish the site."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.admin_inventory import InventoryError, build_inventory


class OutputError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _plain_components(path: Path) -> None:
    for component in (path, *path.parents):
        if component.is_symlink():
            raise OutputError("output_symlink")
        if component.exists() and not component.is_dir():
            raise OutputError("output_parent_not_directory")


def create_preview(source_root: Path, output: Path, baseline_snapshot: Path | None) -> dict:
    root = Path(os.path.abspath(source_root))
    destination = Path(os.path.abspath(output))
    _plain_components(root)
    _plain_components(destination)
    base = root / "output"
    if destination == base or base not in destination.parents:
        raise OutputError("output_outside_ignored_directory")
    if destination.exists():
        raise OutputError("output_exists")
    # Keep output and source operations disjoint. The builder performs no writes.
    snapshot = build_inventory(root, baseline_snapshot)
    if (not isinstance(snapshot, dict) or snapshot.get("schemaVersion") != 1
            or not isinstance(snapshot.get("items"), list)
            or not isinstance(snapshot.get("snapshotToken"), str)
            or not isinstance(snapshot.get("baseline"), dict)
            or snapshot["baseline"].get("status") not in
            {"verified_deployed_artifact", "not_provided"}):
        raise OutputError("inventory_result_invalid")
    result = {"ok": True, "schemaVersion": snapshot["schemaVersion"],
              "items": len(snapshot["items"]), "snapshotToken": snapshot["snapshotToken"],
              "baselineStatus": snapshot["baseline"]["status"], "localPreviewOnly": True}
    payload = (json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if len(payload) > 2_000_000:
        raise OutputError("response_limit")
    assets = Path(__file__).resolve().parents[1] / ".automation/admin-readonly"
    _plain_components(assets)
    source_assets = {name: assets / name for name in ("index.html", "app.js", "style.css")}
    for path in source_assets.values():
        if path.is_symlink() or not path.is_file():
            raise OutputError("preview_asset_missing")
    asset_bytes = {name: path.read_bytes() for name, path in source_assets.items()}
    _plain_components(destination)
    # mkdir is the exclusive claim; an existing folder is never replaced.
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise OutputError("output_exists") from error
    created = []
    try:
        for name, content in ((".keep", b""), ("inventory.json", payload), *asset_bytes.items()):
            path = destination / name
            with path.open("xb") as handle:
                created.append(path)
                handle.write(content)
        if any(path.is_symlink() or path.read_bytes() != asset_bytes[name]
               for name, path in source_assets.items()):
            raise OutputError("preview_asset_changed")
    except Exception:
        # Only this invocation's new files are eligible for cleanup.
        for path in reversed(created):
            path.unlink(missing_ok=True)
        try:
            destination.rmdir()
        except OSError:
            pass
        raise OutputError("output_write_failed") from None
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True,
                        help="new folder below the source checkout's ignored output/")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--baseline-snapshot", type=Path,
                        help="snapshot.json from an already verified local release bundle")
    choice.add_argument("--without-baseline", action="store_true",
                        help="explicitly leave public membership unknown")
    args = parser.parse_args(argv)
    try:
        result = create_preview(args.root, args.output, args.baseline_snapshot)
    except (InventoryError, OutputError) as error:
        print(json.dumps({"ok": False, "reason": error.code}), file=sys.stderr)
        return 2
    except Exception:
        print(json.dumps({"ok": False, "reason": "preview_failed"}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
