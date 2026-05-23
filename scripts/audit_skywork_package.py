#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Finding:
    level: str
    message: str


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def count_pptx_slides(path: Path) -> int | None:
    try:
        with zipfile.ZipFile(path) as archive:
            return sum(
                1
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            )
    except (OSError, zipfile.BadZipFile):
        return None


def count_pdf_pages(path: Path) -> int | None:
    try:
        proc = subprocess.run(
            ["pdfinfo", str(path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def load_status_files(inputs_dir: Path) -> list[dict]:
    statuses: list[dict] = []
    for path in sorted(inputs_dir.glob("*skywork*_status*.json")):
        try:
            payload = json.loads(read_text(path))
        except json.JSONDecodeError:
            payload = {"_parse_error": True}
        payload["_path"] = str(path)
        statuses.append(payload)
    return statuses


def contains_skywork_url(paths: list[Path]) -> bool:
    url_pattern = re.compile(r"https://skywork\.ai/(?:ppt|project|workspace|share|presentation|p)/", re.I)
    return any(url_pattern.search(read_text(path)) for path in paths if path.exists())


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether a topic package has a real Skywork run and no local replacement deck.",
    )
    parser.add_argument("topic_dir", help="Topic package directory, relative to repo root or absolute.")
    args = parser.parse_args(argv)

    topic_dir = Path(args.topic_dir)
    if not topic_dir.is_absolute():
        topic_dir = ROOT / topic_dir
    topic_dir = topic_dir.resolve()

    findings: list[Finding] = []
    if not topic_dir.exists():
        print(f"FAIL topic_dir_missing path={topic_dir}")
        return 2

    inputs_dir = topic_dir / "skywork_inputs"
    exports_dir = topic_dir / "skywork_exports"
    notes_dir = topic_dir / "notes"

    prompt_files = sorted(inputs_dir.glob("*skywork_prompt*.md"))
    if prompt_files:
        findings.append(Finding("PASS", f"prompt_files={len(prompt_files)}"))
    else:
        findings.append(Finding("FAIL", "missing Skywork prompt packet"))

    template_files = sorted(inputs_dir.glob("*.pptx"))
    if any(path.name.lower() == "lgd_template.pptx" for path in template_files):
        findings.append(Finding("PASS", "LGD_Template.pptx present in skywork_inputs"))
    else:
        findings.append(Finding("WARN", "LGD_Template.pptx not found in skywork_inputs"))

    status_files = load_status_files(inputs_dir)
    if status_files:
        findings.append(Finding("PASS", f"automation_status_files={len(status_files)}"))
    else:
        findings.append(Finding("FAIL", "missing Skywork automation status JSON"))

    md_and_json = sorted(inputs_dir.glob("*.md")) + sorted(inputs_dir.glob("*.json")) + sorted(notes_dir.glob("*runlog*.md"))
    if contains_skywork_url(md_and_json):
        findings.append(Finding("PASS", "Skywork project/viewer URL found"))
    else:
        findings.append(Finding("FAIL", "no Skywork project/viewer URL found"))

    pptx_files = sorted(exports_dir.glob("*.pptx"))
    pdf_files = sorted(exports_dir.glob("*.pdf"))
    local_pptx = [path for path in pptx_files if "_local_" in path.name.lower()]
    local_pdf = [path for path in pdf_files if "_local_" in path.name.lower()]
    skywork_pptx = [path for path in pptx_files if "_local_" not in path.name.lower()]
    skywork_pdf = [path for path in pdf_files if "_local_" not in path.name.lower()]

    if local_pptx or local_pdf:
        findings.append(Finding("FAIL", f"forbidden_local_replacement_exports pptx={len(local_pptx)} pdf={len(local_pdf)}"))
    if skywork_pptx and skywork_pdf:
        findings.append(Finding("PASS", f"skywork_exports pptx={len(skywork_pptx)} pdf={len(skywork_pdf)}"))
    else:
        findings.append(Finding("FAIL", "missing non-local Skywork PPTX/PDF export pair"))

    for path in pptx_files:
        slides = count_pptx_slides(path)
        level = "PASS" if slides else "WARN"
        findings.append(Finding(level, f"pptx_slides {path.name}={slides if slides is not None else 'unknown'}"))
    for path in pdf_files:
        pages = count_pdf_pages(path)
        level = "PASS" if pages else "WARN"
        findings.append(Finding(level, f"pdf_pages {path.name}={pages if pages is not None else 'unknown'}"))

    failed = any(finding.level == "FAIL" for finding in findings)
    for finding in findings:
        print(f"{finding.level} {finding.message}")

    if failed:
        print("RESULT blocked: this package does not meet the live Skywork completion bar")
        return 1

    print("RESULT pass: live Skywork completion evidence is present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
