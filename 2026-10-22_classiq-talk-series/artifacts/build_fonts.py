#!/usr/bin/env python3
"""Subset provided OFL Korean fonts with a new family name for this archive.

Set QML_FONT_REGULAR and QML_FONT_BOLD to source font files. Requires fontTools
with Brotli support. No source font path is stored in the output fonts.
"""
import os
import argparse
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "fonts"
OUTPUT.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--regular", default=os.environ.get("QML_FONT_REGULAR"))
parser.add_argument("--bold", default=os.environ.get("QML_FONT_BOLD"))
args = parser.parse_args()
texts = []
for candidate in ROOT.rglob("*.md"):
    if not any(part in {"research", "tmp", "dist", ".venv", ".build"} for part in candidate.parts):
        texts.append(candidate.read_text(encoding="utf-8"))
texts += [path.read_text(encoding="utf-8") for path in (ROOT / "artifacts").glob("*.mjs")]
characters = set("\n".join(texts) + "".join(chr(i) for i in range(32, 127)))
for label, variable, style in [("regular", "QML_FONT_REGULAR", "Regular"),
                                ("bold", "QML_FONT_BOLD", "Bold")]:
    source = args.regular if label == "regular" else args.bold
    if not source:
        raise SystemExit("Set " + variable + " to the source OFL font")
    font = TTFont(source, recalcTimestamp=False)
    for name in list(font["name"].names):
        if name.nameID in {1, 2, 3, 4, 6, 16, 17}:
            font["name"].names.remove(name)
    names = {1: "QML Archive Sans", 2: style,
             3: "QMLArchiveSans-" + style + "-20261020",
             4: "QML Archive Sans " + style, 6: "QMLArchiveSans-" + style,
             16: "QML Archive Sans", 17: style}
    for name_id, value in names.items():
        font["name"].setName(value, name_id, 3, 1, 0x409)
        font["name"].setName(value, name_id, 1, 0, 0)
    options = subset.Options()
    options.name_IDs = ["*"]
    options.name_legacy = True
    options.name_languages = ["*"]
    options.recommended_glyphs = True
    options.notdef_outline = True
    worker = subset.Subsetter(options=options)
    worker.populate(text="".join(sorted(characters)))
    worker.subset(font)
    font.flavor = "woff2"
    destination = OUTPUT / ("qml-sans-" + label + ".woff2")
    font.save(destination)
    print(destination.name, destination.stat().st_size, "bytes")
